from __future__ import annotations
from typing import Any, Dict, Optional
from rag.retrieval.retriever import SimpleRetriever
from rag.generation.answer_generator import generate_answer

def rag_answer(
    query: str,
    crop: Optional[str] = None,
    season: Optional[str] = None,
    location: Optional[Dict[str, Any]] = None,
    memory: Any = None,
) -> Dict[str, Any]:
    retriever = SimpleRetriever()
    contexts = retriever.retrieve(query)
    result = generate_answer(query, contexts)

    recommendations = []
    if crop:
        recommendations.append(f"Keep the advice localized for crop: {crop}.")
    if location:
        recommendations.append("Use the farmer's location for weather and advisory personalization.")
    if season:
        recommendations.append(f"Consider the current season: {season}.")
    if not recommendations:
        recommendations.append("Ask for crop name, location, and growth stage for a better recommendation.")

    return {
        **result,
        "recommendations": recommendations,
        "warnings": [] if contexts else ["Knowledge coverage is low for this question."],
        "contexts": contexts,
    }
