"""
apps/chatbot_orchestrator/main.py
──────────────────────────────────
A chatbot orchestrator.
Routes intents to specialized agents, merges results, and generates
farmer-friendly explanations via LiteLLM.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4

from shared.schemas.chat import AgentResult, ChatRequest, ChatResponse
from shared.utils.logging import get_logger
from shared.llm.client import chat_completion

from apps.chatbot_orchestrator.router.intent_classifier import classify_intent
from apps.chatbot_orchestrator.memory.redis_store import RedisStore
from apps.chatbot_orchestrator.memory.vector_memory import VectorMemory
from apps.chatbot_orchestrator.memory.farm_profile_store import FarmProfileStore
from apps.chatbot_orchestrator.synthesis.aggregator import aggregate_agent_results
from apps.chatbot_orchestrator.synthesis.explainer import explain

from agents.crop.image_analysis.service import analyze_images
from agents.crop.disease_detection.service import detect_disease
from agents.crop.soil_agent.service import analyze_soil
from agents.crop.fertilizer_agent.service import optimize_fertilizer
from agents.crop.weather_agent.service import assess_weather_risk
from agents.crop.crop_planning_agent.service import plan_crops
from agents.market.price_forecast_agent.service import analyze_market
from rag.pipelines.rag_pipeline import rag_answer

logger = get_logger(__name__)

SYNTHESIS_SYSTEM = """You are KrishiMind, a friendly advancedagricultural AI assistant.
Your job is to synthesize analysis from multiple AI agents into ONE clear,
farmer-friendly response in simple language.

Rules:
- Write as if talking directly to a farmer
- Use simple words, avoid technical jargon
- Give specific actionable steps with timing
- Include confidence level naturally ("I'm fairly confident that...")
- Mention costs and quantities when relevant
- Always end with what to do FIRST (most important action)
- Be empathetic and encouraging
- If agent data is missing or low-confidence, say so and give best guess based on available info
- Don't just list agent findings — weave them into a coherent narrative that directly answers the farmer's question
- Keep it concise but complete"""

SYNTHESIS_PROMPT = """Synthesize these agent results into ONE farmer-friendly response:

FARMER QUERY: {query}
INTENT: {intent}
CROP: {crop}
LOCATION: {location}

AGENT FINDINGS:
{agent_summaries}

RECOMMENDATIONS FROM AGENTS:
{all_recommendations}

WARNINGS FROM AGENTS:
{all_warnings}

Write a clear, practical response (200-300 words) that:
1. Directly answers the farmer's question
2. Gives the most important action first
3. Lists 3-5 specific steps with timing
4. Mentions any warnings naturally
5. Ends with a helpful follow-up suggestion"""


@dataclass
class AgentContext:
    farmer_id: str
    crop: Optional[str]
    season: Optional[str]
    growth_stage: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    soil_test_data: Optional[Dict[str, Any]] = None
    fertilizer_context: Optional[Dict[str, Any]] = None


class ChatbotOrchestrator:
    def __init__(self):
        self.memory = RedisStore()
        self.vector_memory = VectorMemory()
        self.profile_store = FarmProfileStore()

    async def handle_message(self, request: ChatRequest) -> ChatResponse:
        t0 = time.perf_counter()
        conversation_id = request.conversation_id or str(uuid4())
        has_images = len(request.images) > 0

        # classify_intent is async and accepts has_images
        decision = await classify_intent(
            request.message,
            history=request.conversation_history,
            has_images=has_images,
        )

        ctx = AgentContext(
            farmer_id=request.farmer_id,
            crop=request.crop,
            season=request.season,
            growth_stage=request.growth_stage,
            location=request.location.model_dump() if request.location else None,
            conversation_history=request.conversation_history,
            images=[img.model_dump() for img in request.images],
            soil_test_data=request.soil_test_data,
            fertilizer_context=request.fertilizer_context, 
        )

        # FarmProfileStore.update() is async — was previously misnamed .upsert()
        if ctx.crop or ctx.location:
            try:
                await self.profile_store.update(ctx.farmer_id, {
                    "crop": ctx.crop,
                    "season": ctx.season,
                    "location": ctx.location,
                })
            except Exception as exc:
                logger.warning("profile_update_skipped", extra={"error": str(exc)})

        logger.info(
            "Intent: %s (%.2f) | Agents: %s | Farmer: %s",
            decision.intent, decision.confidence,
            decision.agents_to_call, ctx.farmer_id,
        )

        # ── Run agents in parallel ─────────────────────────────────────────────
        agent_results: List[AgentResult] = await self._run_agents(decision, ctx, request.message)

        # ── Synthesize with LLM ───────────────────────────────────────────────
        merged = aggregate_agent_results(agent_results)
        answer = await self._synthesize(
            query=request.message,
            intent=decision.intent,
            crop=ctx.crop,
            location=ctx.location,
            agent_results=agent_results,
            merged=merged,
        )

        # ── Follow-up question ────────────────────────────────────────────────
        follow_up = self._generate_follow_up(decision.intent, request)

        # ── Persist memory ────────────────────────────────────────────────────
        # RedisStore.append_message(session_id, role, content) — three separate args
        try:
            await self.memory.append_message(conversation_id, "user", request.message)
            await self.memory.append_message(conversation_id, "assistant", answer)
        except Exception as exc:
            logger.warning("memory_append_skipped", extra={"error": str(exc)})

        elapsed = (time.perf_counter() - t0) * 1000
        logger.info("Response generated in %.1fms", elapsed)

        return ChatResponse(
            conversation_id=conversation_id,
            intent=decision.intent,
            confidence=decision.confidence,
            answer=answer,
            follow_up_question=follow_up,
            recommendations=merged["all_recommendations"][:6],
            warnings=merged["all_warnings"][:4],
            agent_results=agent_results,
            metadata={
                "agent_count": len(agent_results),
                "selected_agents": decision.agents_to_call,
                "latency_ms": round(elapsed, 1),
                "has_images": has_images,
            },
        )

    # ── Agent runner ──────────────────────────────────────────────────────────

    async def _run_agents(
        self,
        decision,
        ctx: AgentContext,
        message: str,
    ) -> List[AgentResult]:
        """Run all required agents in parallel and wrap raw dicts into AgentResult."""
        tasks: Dict[str, Any] = {}
        agents = set(decision.agents_to_call)

        if "image_analysis" in agents:
            tasks["image_analysis"] = self._run_image_analysis(ctx)
        if "disease_detection" in agents:
            tasks["disease_detection"] = self._run_disease_detection(ctx, message)
        if "soil_agent" in agents:
            tasks["soil_agent"] = self._run_soil_agent(ctx, message)
        if "fertilizer_agent" in agents:
            tasks["fertilizer_agent"] = self._run_fertilizer_agent(ctx, message)
        if "weather_agent" in agents:
            tasks["weather_agent"] = self._run_weather_agent(ctx, message)
        if "crop_planning_agent" in agents:
            tasks["crop_planning_agent"] = self._run_crop_planning(ctx, message)
        if "market_agent" in agents:
            tasks["market_agent"] = self._run_market_agent(ctx, message)

        # RAG runs alongside disease detection and general knowledge
        if any(a in agents for a in ["rag_knowledge_agent", "disease_detection", "education_agent"]):
            tasks["rag_knowledge_agent"] = self._run_rag(ctx, message)

        if not tasks:
            tasks["rag_knowledge_agent"] = self._run_rag(ctx, message)

        names = list(tasks.keys())
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        # ── CRITICAL FIX: agents return plain dicts; aggregator needs AgentResult ──
        agent_results: List[AgentResult] = []
        for name, result in zip(names, results):
            if isinstance(result, Exception):
                logger.error("Agent %s failed: %s", name, result)
                agent_results.append(AgentResult(
                    name=name,
                    success=False,
                    error=str(result),
                ))
            else:
                # result is a Dict[str, Any] from the service — wrap into AgentResult
                data: Dict[str, Any] = result or {}
                agent_results.append(AgentResult(
                    name=name,
                    success=True,
                    data=data,
                    # Surface common fields for the aggregator
                    summary=_pick(data, "summary", "answer", "primary_diagnosis"),
                    recommendations=_pick_list(data, "immediate_actions", "recommendations",
                                               "treatment_protocol"),
                    warnings=_pick_list(data, "warnings", "alerts"),
                    confidence=_pick_float(data, "confidence", "confidence_avg"),
                ))

        return agent_results

    # ── Individual agent wrappers ─────────────────────────────────────────────
    # Each method calls the real service function with its EXACT parameter names.

    async def _run_image_analysis(self, ctx: AgentContext) -> Dict[str, Any]:
        # analyze_images(images: List[str], crop_type, context)
        # 'images' expects base64-encoded strings
        b64_images = [
            img.get("base64_data", "")
            for img in ctx.images
            if img.get("base64_data")
        ]
        return await analyze_images(
            images=b64_images,
            crop_type=ctx.crop,
            context=None,
        )

    async def _run_disease_detection(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        # detect_disease(description, crop_type, location, season, growth_stage, image_urls)
        image_urls = [img.get("url", "") for img in ctx.images if img.get("url")]
        return await detect_disease(
            description=message,            # ← 'description', not 'message'
            crop_type=ctx.crop,             # ← 'crop_type', not 'crop'
            location=ctx.location,
            season=ctx.season,
            growth_stage=ctx.growth_stage,
            image_urls=image_urls or None,
        )

    async def _run_soil_agent(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        # analyze_soil(description, crop, season, location)
        return await analyze_soil(
            description=message,
            crop=ctx.crop,
            season=ctx.season,
            location=ctx.location,
            soil_test_data=ctx.soil_test_data,
        )

    async def _run_fertilizer_agent(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        fc = ctx.fertilizer_context or {}

        extra_context = []
        if fc.get("budget"):
            extra_context.append(f"Budget preference: {fc['budget']}")
        if fc.get("organic_preferred"):
            extra_context.append("Farmer strongly prefers organic and bio-fertilizers")

        full_description = message
        if extra_context:
            full_description = message + ". " + ". ".join(extra_context) + "."

        return await optimize_fertilizer(
            crop=ctx.crop,
            season=ctx.season,
            location=ctx.location,
            description=full_description,
            growth_stage=fc.get("growth_stage") or ctx.growth_stage,       # ← NEW
            land_size_acres=float(fc["land_size_acres"])
                            if fc.get("land_size_acres") else None,         # ← NEW
            soil_data={"texture": fc["soil_type"]}
                      if fc.get("soil_type") else None,                     # ← NEW
        )

    async def _run_weather_agent(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        # assess_weather_risk(query, crop, growth_stage, season, location)
        return await assess_weather_risk(
            query=message,                  # ← 'query', not 'message'
            crop=ctx.crop,
            growth_stage=ctx.growth_stage,
            season=ctx.season,
            location=ctx.location,
        )

    async def _run_crop_planning(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        # plan_crops(location, land_size_acres, current_crop, season, ..., description)
        return await plan_crops(
            location=ctx.location,
            current_crop=ctx.crop,
            season=ctx.season,
            description=message,            # ← 'description', not 'message'
        )

    async def _run_market_agent(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        # analyze_market(crop, location, query)
        return await analyze_market(
            crop=ctx.crop,
            location=ctx.location,
            query=message,
        )

    async def _run_rag(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        # rag_answer(query, farm_context, history, top_k)
        farm_context = {
            "location": ctx.location,
            "primary_crops": [ctx.crop] if ctx.crop else [],
            "season": ctx.season,
        }
        return await rag_answer(
            query=message,
            farm_context=farm_context,      # ← 'farm_context', not 'farmer_id'
            history=ctx.conversation_history,  # ← 'history', not 'conversation_history'
        )

    # ── Synthesis ─────────────────────────────────────────────────────────────

    async def _synthesize(
        self,
        query: str,
        intent: str,
        crop: Optional[str],
        location: Optional[Dict[str, Any]],
        agent_results: List[AgentResult],
        merged: Dict[str, Any],
    ) -> str:
        summaries = "\n".join(
            f"- {r.name}: {r.summary}"
            for r in agent_results
            if r.summary
        )
        recommendations = "\n".join(
            f"• {rec}" for rec in merged.get("all_recommendations", [])
        )
        warnings_text = "\n".join(
            f"⚠ {w}" for w in merged.get("all_warnings", [])
        )

        prompt = SYNTHESIS_PROMPT.format(
            query=query,
            intent=intent,
            crop=crop or "not specified",
            location=location or "not specified",
            agent_summaries=summaries or "No agent data available.",
            all_recommendations=recommendations or "None.",
            all_warnings=warnings_text or "None.",
        )

        return await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model_alias="cheap",
            temperature=0.4,
            max_tokens=600,
            system_override=SYNTHESIS_SYSTEM,
        )

    # ── Follow-up suggestions ─────────────────────────────────────────────────

    def _generate_follow_up(self, intent: str, request: ChatRequest) -> Optional[str]:
        follow_ups = {
            "disease_detection":         "Would you like me to suggest a treatment schedule or find a local agrochemist?",
            "soil_analysis":             "Should I also recommend fertilizers based on this soil profile?",
            "fertilizer_recommendation": "Would you like a week-by-week application schedule?",
            "weather_risk":              "Would you like me to set a spray-window alert for the next 7 days?",
            "crop_planning":             "Would you like a full sowing-to-harvest calendar for this crop?",
            "market_intelligence":       "Should I also check the nearest mandi prices for comparison?",
        }
        return follow_ups.get(intent)


# ── Helpers for extracting fields from raw agent dicts ────────────────────────

def _pick(d: Dict[str, Any], *keys: str) -> Optional[str]:
    """Return the first non-empty string value found among the given keys."""
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _pick_list(d: Dict[str, Any], *keys: str) -> List[str]:
    """Return the first non-empty list found among the given keys."""
    for k in keys:
        v = d.get(k)
        if isinstance(v, list) and v:
            return [str(i) for i in v]
        if isinstance(v, str) and v.strip():
            return [v.strip()]
    return []


def _pick_float(d: Dict[str, Any], *keys: str) -> Optional[float]:
    """Return the first numeric value found among the given keys."""
    for k in keys:
        v = d.get(k)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return None