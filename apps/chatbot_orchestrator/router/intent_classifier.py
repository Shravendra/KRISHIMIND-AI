from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class IntentDecision:
    intent: str
    confidence: float
    agents_to_call: List[str]
    needs_more_info: bool = False

def classify_intent(message: str, has_images: bool = False) -> IntentDecision:
    text = message.lower().strip()

    rules: List[Tuple[str, List[str], List[str], float]] = [
        ("crop_disease", ["yellow spots", "leaf", "blight", "fungus", "mildew", "pest"], ["image_analysis", "disease_detection"], 0.93),
        ("soil_health", ["soil", "ph", "npk", "organic matter", "nutrient"], ["soil_agent"], 0.90),
        ("fertilizer_advice", ["fertilizer", "dose", "spray", "manure"], ["fertilizer_agent", "soil_agent"], 0.89),
        ("weather_risk", ["rain", "drought", "heat stress", "flood", "storm"], ["weather_agent"], 0.92),
        ("crop_planning", ["what crop", "rotation", "plan", "sow", "planting"], ["crop_planning_agent"], 0.88),
        ("market_price", ["price", "sell", "market", "commodity"], ["market_agent"], 0.87),
        ("livestock_health", ["cow", "buffalo", "goat", "animal", "livestock"], ["livestock_agent"], 0.84),
        ("education", ["what is", "how does", "teach", "learn"], ["rag_knowledge_agent"], 0.82),
    ]

    for intent, keywords, agents, confidence in rules:
        if any(k in text for k in keywords):
            if has_images and "image_analysis" not in agents:
                agents = ["image_analysis"] + agents
            return IntentDecision(intent=intent, confidence=confidence, agents_to_call=agents, needs_more_info=False)

    if has_images:
        return IntentDecision(
            intent="crop_disease",
            confidence=0.74,
            agents_to_call=["image_analysis", "disease_detection"],
            needs_more_info=False,
        )

    return IntentDecision(
        intent="general_chat",
        confidence=0.55,
        agents_to_call=["rag_knowledge_agent"],
        needs_more_info=False,
    )
