"""Fallback explainer — generates a plain-language answer when the LLM synthesis
call fails or the orchestrator encounters an unexpected error."""

from typing import List, Dict, Any
from shared.schemas.chat import AgentResult
from shared.utils.logging import get_logger

logger = get_logger("synthesis.explainer")


def explain(
    original_message: str,
    results: List[AgentResult],
    error: Exception | None = None,
) -> str:
    """Produce a human-readable fallback response from raw agent results.

    This never calls the LLM — it's pure string assembly so it cannot fail.
    """
    if error:
        logger.error("explainer_invoked_on_error", extra={"error": str(error)})

    if not results:
        return (
            "I wasn't able to retrieve specific agricultural data right now. "
            "Please try rephrasing your question or try again in a moment. "
            "You can also consult your local Krishi Vigyan Kendra (KVK) for immediate advice."
        )

    lines: List[str] = ["Here's what our agricultural experts found:\n"]

    for result in results:
        agent_label = result.name.replace("_", " ").title()
        lines.append(f"**{agent_label}**")

        if result.summary:
            lines.append(result.summary)
        elif result.data:
            # Best-effort extraction of the most important field
            for key in ("disease_name", "soil_health_score", "overall_risk",
                        "market_trend", "primary_recommendation", "message"):
                if key in result.data:
                    lines.append(str(result.data[key]))
                    break

        if result.recommendations:
            lines.append("Recommendations:")
            for rec in result.recommendations[:3]:
                lines.append(f"  • {rec}")

        if result.warnings:
            lines.append("⚠️ Warnings:")
            for warn in result.warnings[:2]:
                lines.append(f"  • {warn}")

        lines.append("")  # blank line between agents

    lines.append(
        "_For personalised guidance, please share your location, crop type, "
        "and a photo of affected plants if applicable._"
    )
    return "\n".join(lines)
