from __future__ import annotations
from typing import Any, Dict, List
from shared.schemas.chat import AgentResult

def aggregate_agent_results(agent_results: List[AgentResult]) -> Dict[str, Any]:
    recommendations: List[str] = []
    warnings: List[str] = []
    evidence: List[Dict[str, Any]] = []

    for result in agent_results:
        data = result.data or {}
        recommendations.extend(data.get("recommendations", []))
        warnings.extend(data.get("warnings", []))
        if data:
            evidence.append({"agent": result.name, "data": data})

    return {
        "recommendations": list(dict.fromkeys(recommendations)),
        "warnings": list(dict.fromkeys(warnings)),
        "evidence": evidence,
    }
