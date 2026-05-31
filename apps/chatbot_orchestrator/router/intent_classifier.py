"""LLM-powered intent classifier — maps user messages to agent intents."""

import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from shared.llm.client import LLMClient
from shared.constants.app import (
    INTENT_DISEASE, INTENT_SOIL, INTENT_FERTILIZER, INTENT_WEATHER,
    INTENT_CROP_PLANNING, INTENT_MARKET, INTENT_LIVESTOCK, INTENT_HARVEST,
    INTENT_KNOWLEDGE, INTENT_GREETING, INTENT_UNKNOWN,
)
from shared.utils.logging import get_logger

logger = get_logger("orchestrator.intent_classifier")
_llm = LLMClient()

# ── IntentDecision dataclass ──────────────────────────────────────────────────

@dataclass
class IntentDecision:
    """Structured result returned by classify_intent."""
    intent: str
    confidence: float
    agents_to_call: List[str] = field(default_factory=list)
    secondary_intents: List[str] = field(default_factory=list)
    extracted_entities: Dict[str, Any] = field(default_factory=dict)


# ── Intent → Agents mapping ───────────────────────────────────────────────────

INTENT_TO_AGENTS: Dict[str, List[str]] = {
    INTENT_DISEASE:        ["image_analysis", "disease_detection", "rag_knowledge_agent"],
    INTENT_SOIL:           ["soil_agent", "rag_knowledge_agent"],
    INTENT_FERTILIZER:     ["fertilizer_agent", "soil_agent"],
    INTENT_WEATHER:        ["weather_agent"],
    INTENT_CROP_PLANNING:  ["crop_planning_agent", "weather_agent"],
    INTENT_MARKET:         ["market_agent"],
    INTENT_HARVEST:        ["harvest_agent", "postharvest_agent", "weather_agent"],
    INTENT_LIVESTOCK:      ["rag_knowledge_agent"],
    INTENT_KNOWLEDGE:      ["rag_knowledge_agent"],
    INTENT_GREETING:       ["rag_knowledge_agent"],
    INTENT_UNKNOWN:        ["rag_knowledge_agent"],
}


def _agents_for_intent(primary: str, secondary: List[str], has_images: bool) -> List[str]:
    """Build the deduplicated agent list from intents + image flag."""
    agents: List[str] = list(INTENT_TO_AGENTS.get(primary, ["rag_knowledge_agent"]))
    for intent in secondary:
        for agent in INTENT_TO_AGENTS.get(intent, []):
            if agent not in agents:
                agents.append(agent)
    # If images were uploaded and disease / image_analysis not already queued, add them
    if has_images and "image_analysis" not in agents:
        agents.insert(0, "image_analysis")
    return agents


INTENT_SYSTEM_PROMPT = """You are an intent classifier for an agricultural AI assistant serving Indian farmers.

Given a user message, identify which agricultural domain(s) are most relevant.
Return ONLY a JSON object — no prose, no markdown fences.

Available intents (you may return multiple if the query spans domains):
- disease_detection   : plant diseases, pests, leaf spots, yellowing, wilting, image upload
- soil_analysis       : soil pH, NPK, EC, micronutrients, soil test results
- fertilizer_recommendation : fertilizer type, dose, schedule, organic/chemical
- weather_risk        : rain forecast, drought, frost, irrigation timing, spraying window
- crop_planning       : which crop to grow, sowing calendar, crop rotation, intercropping
- market_intelligence : mandi price, MSP, selling strategy, price forecast
- livestock_health    : cattle, poultry, goat disease, vaccination, feed
- harvest_recommendation : optimal harvest timing, methods, yield estimation
- postharvest_management : handling, storage, preservation of agricultural produce
- general_knowledge   : farming tips, government schemes, organic farming practices
- greeting            : hello, hi, greetings, thanks, general chitchat
- unknown             : cannot determine

Response format:
{
  "primary_intent": "<intent>",
  "secondary_intents": ["<intent>", ...],
  "confidence": 0.0-1.0,
  "extracted_entities": {
    "crop": "<crop name or null>",
    "location": "<state/district or null>",
    "has_image": true/false,
    "urgency": "high|medium|low"
  }
}"""

# ── Lightweight keyword fallback ──────────────────────────────────────────────

KEYWORD_MAP: Dict[str, str] = {
    # Disease
    "disease": INTENT_DISEASE, "fungal": INTENT_DISEASE, "bacterial": INTENT_DISEASE,
    "pest": INTENT_DISEASE, "insect": INTENT_DISEASE, "spot": INTENT_DISEASE,
    "wilt": INTENT_DISEASE, "blight": INTENT_DISEASE, "rot": INTENT_DISEASE,
    "yellow": INTENT_DISEASE, "brown": INTENT_DISEASE, "leaf": INTENT_DISEASE,
    # Soil
    "soil": INTENT_SOIL, "ph": INTENT_SOIL, "npk": INTENT_SOIL,
    "nitrogen": INTENT_SOIL, "phosphorus": INTENT_SOIL, "potassium": INTENT_SOIL,
    "ec ": INTENT_SOIL, "micronutrient": INTENT_SOIL,
    # Fertilizer
    "fertilizer": INTENT_FERTILIZER, "fertiliser": INTENT_FERTILIZER,
    "urea": INTENT_FERTILIZER, "dap": INTENT_FERTILIZER, "compost": INTENT_FERTILIZER,
    "manure": INTENT_FERTILIZER, "dose": INTENT_FERTILIZER,
    # Weather
    "rain": INTENT_WEATHER, "weather": INTENT_WEATHER, "drought": INTENT_WEATHER,
    "irrigation": INTENT_WEATHER, "spray": INTENT_WEATHER, "frost": INTENT_WEATHER,
    "temperature": INTENT_WEATHER, "monsoon": INTENT_WEATHER,
    # Crop planning
    "sow": INTENT_CROP_PLANNING, "plant": INTENT_CROP_PLANNING, "grow": INTENT_CROP_PLANNING,
    "rotation": INTENT_CROP_PLANNING, "intercrop": INTENT_CROP_PLANNING,
    "season": INTENT_CROP_PLANNING, "variety": INTENT_CROP_PLANNING, "seed": INTENT_CROP_PLANNING,
    # Market
    "price": INTENT_MARKET, "mandi": INTENT_MARKET, "market": INTENT_MARKET,
    "sell": INTENT_MARKET, "msp": INTENT_MARKET, "profit": INTENT_MARKET,
    "rate": INTENT_MARKET,
    # Harvest
    "harvest" : INTENT_HARVEST, "yield" : INTENT_HARVEST, "maturity" : INTENT_HARVEST,
    "panicle" : INTENT_HARVEST, "grain" : INTENT_HARVEST, "lodge" : INTENT_HARVEST,
    "postharvest": INTENT_HARVEST, "storage": INTENT_HARVEST, "preservation": INTENT_HARVEST,
    # Livestock
    "cow": INTENT_LIVESTOCK, "cattle": INTENT_LIVESTOCK, "buffalo": INTENT_LIVESTOCK,
    "goat": INTENT_LIVESTOCK, "poultry": INTENT_LIVESTOCK, "chicken": INTENT_LIVESTOCK,
    "animal": INTENT_LIVESTOCK, "feed": INTENT_LIVESTOCK, "milk": INTENT_LIVESTOCK,
    "vaccine": INTENT_LIVESTOCK,
    # Greeting
    "hello": INTENT_GREETING, "hi": INTENT_GREETING, "hey": INTENT_GREETING,
    "namaste": INTENT_GREETING, "thanks": INTENT_GREETING, "thank": INTENT_GREETING,
}


def _keyword_classify(message: str) -> str:
    lower = message.lower()
    scores: Dict[str, int] = {}
    for kw, intent in KEYWORD_MAP.items():
        if kw in lower:
            scores[intent] = scores.get(intent, 0) + 1
    if not scores:
        return INTENT_UNKNOWN
    return max(scores, key=scores.__getitem__)


# ── Public API ────────────────────────────────────────────────────────────────

async def classify_intent(
    message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    has_images: bool = False,
) -> IntentDecision:
    """Classify the user message into one or more agricultural intents.

    Args:
        message:    The farmer's input text.
        history:    Optional recent conversation turns for context.
        has_images: Whether the request includes uploaded images.

    Returns:
        IntentDecision with intent, confidence, and agents_to_call populated.
    """
    try:
        messages = []
        if history:
            for turn in history[-3:]:
                messages.append({
                    "role": turn.get("role", "user"),
                    "content": turn.get("content", ""),
                })
        # Append image hint to the message so the LLM knows
        user_content = message
        if has_images:
            user_content = f"[Image uploaded] {message}"
        messages.append({"role": "user", "content": user_content})

        raw = await _llm.chat_completion(
            messages=messages,
            system_prompt=INTENT_SYSTEM_PROMPT,
            model_alias="fast",
            temperature=0.1,
            max_tokens=300,
        )

        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        result = json.loads(cleaned)

        primary = result.get("primary_intent", INTENT_UNKNOWN)
        secondary = result.get("secondary_intents", [])
        confidence = float(result.get("confidence", 0.7))
        entities = result.get("extracted_entities", {})

        # Propagate has_images into entities
        if has_images:
            entities["has_image"] = True

        agents = _agents_for_intent(primary, secondary, has_images)

        logger.info(
            "intent_classified",
            extra={
                "intent": primary,
                "confidence": confidence,
                "agents": agents,
                "message_len": len(message),
            },
        )

        return IntentDecision(
            intent=primary,
            confidence=confidence,
            agents_to_call=agents,
            secondary_intents=secondary,
            extracted_entities=entities,
        )

    except Exception as exc:
        logger.warning("intent_classifier_fallback", extra={"error": str(exc)})
        primary = _keyword_classify(message)
        agents = _agents_for_intent(primary, [], has_images)
        return IntentDecision(
            intent=primary,
            confidence=0.6,
            agents_to_call=agents,
            secondary_intents=[],
            extracted_entities={
                "crop": None,
                "location": None,
                "has_image": has_images,
                "urgency": "medium",
            },
        )