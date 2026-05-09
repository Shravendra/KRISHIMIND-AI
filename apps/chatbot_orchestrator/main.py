from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4
from typing import Any, Dict, List

from shared.schemas.chat import ChatRequest, ChatResponse, AgentResult
from shared.utils.logging import get_logger
from apps.chatbot_orchestrator.router.intent_classifier import classify_intent
from apps.chatbot_orchestrator.memory.redis_store import RedisStore
from apps.chatbot_orchestrator.memory.vector_memory import VectorMemory
from apps.chatbot_orchestrator.memory.farm_profile_store import FarmProfileStore
from apps.chatbot_orchestrator.synthesis.aggregator import aggregate_agent_results
from apps.chatbot_orchestrator.synthesis.explainer import explain
from rag.pipelines.rag_pipeline import rag_answer
from agents.crop.image_analysis.service import analyze_images

logger = get_logger(__name__)

@dataclass
class AgentContext:
    farmer_id: str
    crop: str | None
    season: str | None
    location: Dict[str, Any] | None
    conversation_history: List[Dict[str, Any]]
    images: List[Dict[str, Any]]

class ChatbotOrchestrator:
    def __init__(self):
        self.memory = RedisStore()
        self.vector_memory = VectorMemory()
        self.profile_store = FarmProfileStore()

    async def handle_message(self, request: ChatRequest) -> ChatResponse:
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

        agent_results: List[AgentResult] = []
        if "image_analysis" in decision.agents_to_call:
            image_result = analyze_images(
                image_inputs=ctx.images,
                crop_type=ctx.crop,
                location=ctx.location,
            )
            agent_results.append(AgentResult(name="image_analysis", success=True, data=image_result))

        if any(a.endswith("_agent") or a in {"rag_knowledge_agent", "disease_detection"} for a in decision.agents_to_call):
            rag_result = rag_answer(
                query=request.message,
                crop=request.crop,
                season=request.season,
                location=ctx.location,
                memory=self.vector_memory,
            )
            agent_results.append(AgentResult(name="rag_knowledge_agent", success=True, data=rag_result))

        merged = aggregate_agent_results(agent_results)
        recommendations = merged["recommendations"]
        warnings = merged["warnings"]

        summary = (
            f"Intent detected: {decision.intent}. "
            f"Confidence: {decision.confidence:.2f}. "
            f"Relevant signals were combined from the available agents."
        )

        follow_up = None
        if decision.intent == "crop_disease" and not request.images:
            follow_up = "Please upload a clear leaf photo from the top and underside for a better diagnosis."
        elif decision.intent == "weather_risk" and not request.location:
            follow_up = "Share your village or field location so I can make the weather advice more localized."

        answer = explain(
            intent=decision.intent,
            summary=summary,
            recommendations=recommendations or ["Keep monitoring the crop and check for changes over the next 24-48 hours."],
            warnings=warnings,
            follow_up_question=follow_up,
        )

        metadata = {
            "agent_count": len(agent_results),
            "selected_agents": decision.agents_to_call,
        }

        await self.memory.append_message(conversation_id, {"role": "user", "content": request.message})
        await self.memory.append_message(conversation_id, {"role": "assistant", "content": answer})

        return ChatResponse(
            conversation_id=conversation_id,
            intent=decision.intent,
            confidence=decision.confidence,
            answer=answer,
            follow_up_question=follow_up,
            recommendations=recommendations,
            warnings=warnings,
            agent_results=agent_results,
            metadata=metadata,
        )
