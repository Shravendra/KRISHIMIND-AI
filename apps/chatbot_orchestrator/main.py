"""
apps/chatbot_orchestrator/main.py
──────────────────────────────────
Production-grade chatbot orchestrator.
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

SYNTHESIS_SYSTEM = """You are KrishiMind, a friendly agricultural AI assistant.
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


class ChatbotOrchestrator:
    def __init__(self):
        self.memory = RedisStore()
        self.vector_memory = VectorMemory()
        self.profile_store = FarmProfileStore()

    async def handle_message(self, request: ChatRequest) -> ChatResponse:
        t0 = time.perf_counter()
        conversation_id = request.conversation_id or str(uuid4())
        has_images = len(request.images) > 0
        decision = classify_intent(request.message, has_images=has_images)

        ctx = AgentContext(
            farmer_id=request.farmer_id,
            crop=request.crop,
            season=request.season,
            location=request.location.model_dump() if request.location else None,
            conversation_history=request.conversation_history,
            images=[img.model_dump() for img in request.images],
        )

        # Update farm profile with context
        if ctx.crop or ctx.location:
            self.profile_store.upsert(ctx.farmer_id, {
                "crop": ctx.crop,
                "season": ctx.season,
                "location": ctx.location,
            })

        logger.info(
            "Intent: %s (%.2f) | Agents: %s | Farmer: %s",
            decision.intent, decision.confidence,
            decision.agents_to_call, ctx.farmer_id
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
        await self.memory.append_message(conversation_id, {"role": "user", "content": request.message})
        await self.memory.append_message(conversation_id, {"role": "assistant", "content": answer})

        elapsed = (time.perf_counter() - t0) * 1000
        logger.info("Response generated in %.1fms", elapsed)

        return ChatResponse(
            conversation_id=conversation_id,
            intent=decision.intent,
            confidence=decision.confidence,
            answer=answer,
            follow_up_question=follow_up,
            recommendations=merged["recommendations"][:6],
            warnings=merged["warnings"][:4],
            agent_results=agent_results,
            metadata={
                "agent_count": len(agent_results),
                "selected_agents": decision.agents_to_call,
                "latency_ms": round(elapsed, 1),
                "has_images": has_images,
            },
        )

    async def _run_agents(
        self,
        decision,
        ctx: AgentContext,
        message: str,
    ) -> List[AgentResult]:
        """Run all required agents in parallel."""
        tasks = {}

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

        # Always run RAG for educational context
        if any(a in agents for a in ["rag_knowledge_agent", "disease_detection", "education_agent"]):
            tasks["rag_knowledge_agent"] = self._run_rag(ctx, message)

        if not tasks:
            tasks["rag_knowledge_agent"] = self._run_rag(ctx, message)

        # Execute all tasks in parallel
        names = list(tasks.keys())
        coroutines = list(tasks.values())
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        agent_results = []
        for name, result in zip(names, results):
            if isinstance(result, Exception):
                logger.error("Agent %s failed: %s", name, result)
                agent_results.append(AgentResult(
                    name=name, success=False, error=str(result)
                ))
            else:
                agent_results.append(AgentResult(
                    name=name, success=True, data=result or {}
                ))

        return agent_results

    # ── Agent runners ──────────────────────────────────────────────────────────

    async def _run_image_analysis(self, ctx: AgentContext) -> Dict[str, Any]:
        return await analyze_images(
            images=[img.get("base64_data", img.get("url", "")) for img in ctx.images],
            crop_type=ctx.crop,
            context=None,
        )

    async def _run_disease_detection(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        image_urls = [img.get("url", "") for img in ctx.images if img.get("url")]
        return await detect_disease(
            description=message,
            crop_type=ctx.crop,
            location=ctx.location,
            season=ctx.season,
            image_urls=image_urls if image_urls else None,
        )

    async def _run_soil_agent(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        return await analyze_soil(
            description=message,
            crop=ctx.crop,
            season=ctx.season,
            location=ctx.location,
        )

    async def _run_fertilizer_agent(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        return await optimize_fertilizer(
            crop=ctx.crop,
            season=ctx.season,
            location=ctx.location,
            description=message,
        )

    async def _run_weather_agent(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        return await assess_weather_risk(
            query=message,
            crop=ctx.crop,
            season=ctx.season,
            location=ctx.location,
        )

    async def _run_crop_planning(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        return await plan_crops(
            location=ctx.location,
            current_crop=ctx.crop,
            season=ctx.season,
            description=message,
        )

    async def _run_market_agent(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        return await analyze_market(
            crop=ctx.crop,
            location=ctx.location,
            query=message,
        )

    async def _run_rag(self, ctx: AgentContext, message: str) -> Dict[str, Any]:
        return rag_answer(
            query=message,
            crop=ctx.crop,
            season=ctx.season,
            location=ctx.location,
            memory=self.vector_memory,
        )

    # ── Synthesis ──────────────────────────────────────────────────────────────

    async def _synthesize(
        self,
        query: str,
        intent: str,
        crop: Optional[str],
        location: Optional[Dict],
        agent_results: List[AgentResult],
        merged: Dict[str, Any],
    ) -> str:
        """Use LLM to synthesize multi-agent outputs into farmer-friendly response."""

        # Build agent summaries
        summaries = []
        for r in agent_results:
            if r.success and r.data:
                summary = r.data.get("summary") or r.data.get("primary_diagnosis") or str(r.data)[:200]
                summaries.append(f"[{r.name}]: {summary}")

        loc_str = "India"
        if location:
            parts = [location.get("state"), location.get("country", "India")]
            loc_str = ", ".join(p for p in parts if p)

        prompt = SYNTHESIS_PROMPT.format(
            query=query,
            intent=intent,
            crop=crop or "general crops",
            location=loc_str,
            agent_summaries="\n".join(summaries) if summaries else "No specific agent data",
            all_recommendations="\n".join(f"• {r}" for r in merged.get("recommendations", [])[:8]),
            all_warnings="\n".join(f"⚠ {w}" for w in merged.get("warnings", [])[:4]),
        )

        try:
            answer = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model_alias="cheap",
                system_override=SYNTHESIS_SYSTEM,
                temperature=0.4,
                max_tokens=600,
            )
            return answer
        except Exception as e:
            logger.error("Synthesis failed: %s", e)
            # Fallback to rule-based explainer
            return explain(
                intent=intent,
                summary=f"Analysis complete for: {query}",
                recommendations=merged.get("recommendations", []),
                warnings=merged.get("warnings", []),
            )

    def _generate_follow_up(self, intent: str, request: ChatRequest) -> Optional[str]:
        """Generate context-appropriate follow-up questions."""
        follow_ups = {
            "crop_disease": (
                "Please upload a clear photo of the affected leaves (both top and underside) "
                "for a more precise diagnosis."
                if not request.images else
                "Would you like me to calculate the exact pesticide quantity for your field size?"
            ),
            "soil_health": "Do you have a Soil Health Card or recent soil test report I can analyze?",
            "fertilizer_advice": "What is your field size in acres so I can calculate exact quantities?",
            "weather_risk": "Share your precise location (village/district) for hyper-local weather alerts.",
            "crop_planning": "What is your water source — borewell, canal, or rain-fed?",
            "market_price": "How many quintals do you expect to harvest, and do you have storage available?",
            "livestock_health": "How many animals are affected and for how long have you noticed symptoms?",
        }
        return follow_ups.get(intent)
