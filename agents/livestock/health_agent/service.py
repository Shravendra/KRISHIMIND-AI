"""Livestock Health Agent — diagnoses animal health issues and recommends treatments."""

import json
import re
from typing import List, Optional, Dict, Any

from shared.llm.client import LLMClient
from shared.schemas.chat import AgentResult
from shared.utils.logging import get_logger

logger = get_logger("agents.livestock_health")
_llm = LLMClient()

LIVESTOCK_SYSTEM_PROMPT = """You are an expert veterinarian and livestock specialist with 20+ years of experience serving Indian farmers.
You specialise in cattle, buffalo, goat, sheep, poultry, and pig health.

When asked about animal health, respond ONLY with a valid JSON object in this exact format:
{
  "animal_type": "<cattle|buffalo|goat|sheep|poultry|pig|other>",
  "condition_assessment": "<healthy|mild_issue|moderate_issue|serious|critical>",
  "possible_conditions": [
    {
      "name": "<disease/condition name>",
      "confidence": 0.0-1.0,
      "symptoms_match": ["<matching symptom>", ...],
      "transmission_risk": "low|medium|high",
      "zoonotic": true/false
    }
  ],
  "immediate_actions": ["<action 1>", ...],
  "treatment": {
    "medications": [
      {
        "name": "<medicine name>",
        "type": "antibiotic|antifungal|antiparasitic|supportive|vaccine",
        "dose": "<dose and frequency>",
        "duration": "<duration>",
        "availability": "veterinary_prescription|otc|government_supply"
      }
    ],
    "home_remedies": ["<traditional/herbal remedy>", ...],
    "supportive_care": ["<care instruction>", ...]
  },
  "nutrition_recommendations": {
    "feed_adjustments": ["<adjustment>", ...],
    "supplements": ["<supplement>", ...],
    "water_requirements": "<daily water requirement>"
  },
  "vaccination_status_check": ["<vaccine to verify>", ...],
  "when_to_call_vet": "<condition requiring emergency vet>",
  "government_schemes": [
    {
      "scheme": "<scheme name>",
      "benefit": "<what it provides>",
      "how_to_access": "<department/helpline>"
    }
  ],
  "biosecurity_measures": ["<measure>", ...],
  "economic_impact": "<estimated production loss and recovery timeline>",
  "follow_up_timeline": "<when to reassess>",
  "summary": "<2-3 sentence plain summary for the farmer>"
}

Include references to schemes like PMMSY, Rashtriya Gokul Mission, National Livestock Mission where applicable.
For critical conditions always emphasise calling a government veterinarian (toll-free 1962)."""


class LivestockHealthAgent:
    """Diagnoses livestock health problems and recommends veterinary interventions."""

    async def assess_health(
        self,
        query: str,
        animal_type: Optional[str] = None,
        symptoms: Optional[List[str]] = None,
        farm_context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Run the livestock health assessment.

        Args:
            query:        Natural-language description of the problem.
            animal_type:  Optional hint (e.g. "cattle", "poultry").
            symptoms:     Optional pre-extracted symptom list.
            farm_context: Farm profile dict (location, herd size, etc.).

        Returns:
            AgentResult with diagnosis, treatment plan, and recommendations.
        """
        farm_ctx = farm_context or {}
        symptom_text = ", ".join(symptoms) if symptoms else "not specified"
        animal_hint = animal_type or farm_ctx.get("primary_livestock", "not specified")

        user_prompt = f"""Farmer's query: {query}

Animal type: {animal_hint}
Reported symptoms: {symptom_text}
Location: {farm_ctx.get("location", "India")}
Herd/flock size: {farm_ctx.get("livestock_count", "unknown")}
Previous health issues: {farm_ctx.get("livestock_history", "none mentioned")}

Please provide a comprehensive livestock health assessment."""

        try:
            raw = await _llm.chat_completion(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=LIVESTOCK_SYSTEM_PROMPT,
                model_alias="reasoning",
                temperature=0.2,
                max_tokens=1400,
            )

            cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
            data = json.loads(cleaned)

            condition = data.get("condition_assessment", "unknown")
            is_serious = condition in ("serious", "critical")

            recs = list(data.get("immediate_actions", []))
            for med in data.get("treatment", {}).get("medications", []):
                recs.append(f"Use {med['name']}: {med.get('dose', '')}")
            for adj in data.get("nutrition_recommendations", {}).get("feed_adjustments", []):
                recs.append(adj)

            warnings = []
            if is_serious:
                warnings.append(f"⚠️ {condition.upper()} condition detected — contact a veterinarian immediately (toll-free: 1962)")
            for cond in data.get("possible_conditions", []):
                if cond.get("zoonotic"):
                    warnings.append(f"⚠️ {cond['name']} may be transmissible to humans — take precautions")
                if cond.get("transmission_risk") == "high":
                    warnings.append(f"High spread risk: isolate affected animals immediately")

            confidence = 0.5
            if data.get("possible_conditions"):
                confidence = max(c.get("confidence", 0.5) for c in data["possible_conditions"])

            summary = data.get("summary", f"Livestock health assessment complete. Condition: {condition}.")

            logger.info(
                "livestock_assessment_complete",
                extra={
                    "animal_type": data.get("animal_type"),
                    "condition": condition,
                    "conditions_detected": len(data.get("possible_conditions", [])),
                },
            )

            return AgentResult(
                name="livestock_health",
                success=True,
                data=data,
                summary=summary,
                recommendations=recs[:8],
                warnings=warnings,
                confidence=confidence,
            )

        except json.JSONDecodeError:
            return AgentResult(
                name="livestock_health",
                success=True,
                data={"raw_response": raw[:800] if raw else ""},
                summary=raw[:300] if raw else "Livestock assessment completed.",
                recommendations=["Consult a local veterinarian for a definitive diagnosis."],
                warnings=[],
                confidence=0.4,
            )
        except Exception as exc:
            logger.error("livestock_agent_error", extra={"error": str(exc)})
            return AgentResult(
                name="livestock_health",
                success=False,
                data={},
                summary="Livestock health assessment temporarily unavailable.",
                recommendations=[
                    "Call the livestock helpline at 1962 for immediate assistance.",
                    "Isolate sick animals from the rest of the herd/flock.",
                ],
                warnings=["Unable to complete AI diagnosis — please seek veterinary help."],
                confidence=0.0,
            )
