"""LLM-powered intent classifier — maps user messages to agent intents."""

import json
import re
from typing import List, Dict, Any

from shared.llm.client import LLMClient
from shared.constants.app import (
    INTENT_DISEASE, INTENT_SOIL, INTENT_FERTILIZER, INTENT_WEATHER,
    INTENT_CROP_PLANNING, INTENT_MARKET, INTENT_LIVESTOCK,
    INTENT_KNOWLEDGE, INTENT_GREETING, INTENT_UNKNOWN,
)
from shared.utils.logging import get_logger

logger = get_logger("orchestrator.intent_classifier")
_llm = LLMClient()

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
- general_knowledge   : farming tips, government schemes, organic farming practices
- greeting            : hello, hi, greetings, thanks, general chitchat
- unknown             : cannot determine

Response format:
{
  "primary_intent": "<intent>",
  "secondary_intents": ["<intent>", ...],   // 0-2 additional relevant intents
  "confidence": 0.0-1.0,
  "extracted_entities": {
    "crop": "<crop name or null>",
    "location": "<state/district or null>",
    "has_image": true/false,
    "urgency": "high|medium|low"
  }
}"""

# Lightweight keyword-based fallback (no LLM call)
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
    "rotation": INTENT_CROP_PLANNING, "intercrop": INTENT_CROP_PLANNING, "season": INTENT_CROP_PLANNING,
    "variety": INTENT_CROP_PLANNING, "seed": INTENT_CROP_PLANNING,
    # Market
    "price": INTENT_MARKET, "mandi": INTENT_MARKET, "market": INTENT_MARKET,
    "sell": INTENT_MARKET, "msp": INTENT_MARKET, "profit": INTENT_MARKET,
    "rate": INTENT_MARKET,
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


async def classify_intent(message: str, history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Classify the user message into one or more agricultural intents.

    Uses LLM for precision; falls back to keyword matching on failure.
    """
    try:
        messages = []
        if history:
            # Include last 3 turns for context
            for turn in history[-3:]:
                messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})
        messages.append({"role": "user", "content": message})

        raw = await _llm.chat_completion(
            messages=messages,
            system_prompt=INTENT_SYSTEM_PROMPT,
            model_alias="fast",
            temperature=0.1,
            max_tokens=300,
        )

        # Strip any accidental markdown fences
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        result = json.loads(cleaned)

        logger.info(
            "intent_classified",
            extra={
                "intent": result.get("primary_intent"),
                "confidence": result.get("confidence"),
                "message_len": len(message),
            },
        )
        return result

    except Exception as exc:
        logger.warning("intent_classifier_fallback", extra={"error": str(exc)})
        primary = _keyword_classify(message)
        return {
            "primary_intent": primary,
            "secondary_intents": [],
            "confidence": 0.6,
            "extracted_entities": {
                "crop": None,
                "location": None,
                "has_image": False,
                "urgency": "medium",
            },
        }
