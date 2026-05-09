from __future__ import annotations
from typing import List, Optional

def explain(
    intent: str,
    summary: str,
    recommendations: List[str],
    warnings: List[str],
    follow_up_question: Optional[str] = None,
) -> str:
    lines = []
    if intent == "crop_disease":
        lines.append("I reviewed your crop issue and here is the practical advice.")
    elif intent == "weather_risk":
        lines.append("I checked the weather risk and prepared a simple action plan.")
    else:
        lines.append("Here is a farmer-friendly response based on your question.")

    lines.append(summary)

    if recommendations:
        lines.append("Recommended actions:")
        for idx, item in enumerate(recommendations, 1):
            lines.append(f"{idx}. {item}")

    if warnings:
        lines.append("Warnings:")
        for item in warnings:
            lines.append(f"- {item}")

    if follow_up_question:
        lines.append(follow_up_question)

    return "\n".join(lines)
