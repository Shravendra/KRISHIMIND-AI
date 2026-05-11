"""Aggregates results from multiple agents into a unified context for synthesis."""

from typing import List, Dict, Any
from shared.schemas.chat import AgentResult
from shared.utils.logging import get_logger

logger = get_logger("synthesis.aggregator")


def aggregate_agent_results(results: List[AgentResult]) -> Dict[str, Any]:
    """Merge multiple AgentResult objects into a single synthesis context.

    Returns a dict that the LLM synthesis prompt will receive as context,
    with all recommendations, warnings, and structured data consolidated.
    """
    if not results:
        return {
            "agents_used": [],
            "combined_analysis": {},
            "all_recommendations": [],
            "all_warnings": [],
            "key_data_points": [],
            "confidence_avg": 0.0,
        }

    all_recommendations: List[str] = []
    all_warnings: List[str] = []
    key_data_points: List[Dict] = []
    combined_analysis: Dict[str, Any] = {}
    confidence_scores: List[float] = []

    for result in results:
        agent_id = result.name

        # Collect flat lists
        all_recommendations.extend(result.recommendations or [])
        all_warnings.extend(result.warnings or [])
        confidence_scores.append(result.confidence or 0.5)

        # Store per-agent structured data
        if result.data:
            combined_analysis[agent_id] = result.data

            # Extract headline data points for easy LLM consumption
            for field in ("disease_name", "severity", "soil_health_score",
                          "overall_risk", "market_trend", "primary_recommendation"):
                if field in result.data:
                    key_data_points.append({
                        "agent": agent_id,
                        "field": field,
                        "value": result.data[field],
                    })

    # Deduplicate while preserving order
    seen_rec: set = set()
    unique_recs = []
    for r in all_recommendations:
        if r not in seen_rec:
            seen_rec.add(r)
            unique_recs.append(r)

    seen_warn: set = set()
    unique_warns = []
    for w in all_warnings:
        if w not in seen_warn:
            seen_warn.add(w)
            unique_warns.append(w)

    # Sort warnings: put "high severity" / "critical" / "urgent" first
    priority_keywords = {"critical", "urgent", "high", "immediately", "severe"}
    unique_warns.sort(
        key=lambda w: any(kw in w.lower() for kw in priority_keywords),
        reverse=True,
    )

    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5

    return {
        "agents_used": [r.name for r in results],
        "combined_analysis": combined_analysis,
        "all_recommendations": unique_recs[:10],   # cap at 10
        "all_warnings": unique_warns[:5],           # cap at 5
        "key_data_points": key_data_points,
        "confidence_avg": round(avg_confidence, 2),
    }
