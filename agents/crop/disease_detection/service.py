"""
agents/crop/disease_detection/service.py
─────────────────────────────────────────
Crop disease & pest identification agent.
Uses vision LLM for image analysis + RAG for treatment protocols.
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from shared.llm.client import chat_completion, vision_completion
from shared.utils.logging import get_logger

logger = get_logger(__name__)

DISEASE_SYSTEM_PROMPT = """You are an expert plant pathologist and agronomist specializing in crop disease diagnosis.
You have deep knowledge of:
- Fungal diseases (blight, rust, mildew, anthracnose, wilt)
- Bacterial diseases (leaf spot, canker, blight)
- Viral diseases (mosaic, yellowing, stunting)
- Pest infestations (aphids, mites, whitefly, stem borer)
- Nutritional deficiencies (N, P, K, Fe, Mg, Ca)

When diagnosing:
1. Identify the most likely disease/pest based on symptoms
2. Provide confidence level (0-1)
3. List differential diagnoses (alternative possibilities)
4. Give severity assessment: low | medium | high | critical
5. Recommend immediate actions (within 24 hours)
6. Suggest preventive measures
7. Specify which fungicide/pesticide to use with exact dosage
8. Warn about withholding periods before harvest
9. Flag any organic/non-chemical alternatives

Always be farmer-friendly: use simple language, give specific product names available in India,
and include approximate cost where possible."""

VISION_DISEASE_PROMPT = """Analyze this crop image carefully and provide a detailed disease/pest diagnosis.

Crop type: {crop_type}
Location: {location}
Season: {season}
Growth stage: {growth_stage}
Farmer's description: {description}

Please provide:
1. PRIMARY DIAGNOSIS: Most likely disease/pest with confidence (0-100%)
2. SYMPTOMS OBSERVED: What you can see in the image
3. SEVERITY: low / medium / high / critical
4. DIFFERENTIAL DIAGNOSES: 2-3 other possibilities
5. IMMEDIATE ACTIONS (next 24-48 hours)
6. TREATMENT PROTOCOL: Specific fungicide/pesticide, dosage, application method
7. ORGANIC ALTERNATIVES: Non-chemical options
8. PREVENTIVE MEASURES: For future seasons
9. FOLLOW-UP: When to reassess and what to look for
10. WARNINGS: Any precautions (harvest interval, mixing restrictions, etc.)

Format your response as structured JSON."""

TEXT_DISEASE_PROMPT = """A farmer reports the following crop problem:

Crop: {crop_type}
Location: {location}
Season: {season}
Growth Stage: {growth_stage}
Symptoms described: {description}

Based on these symptoms, provide a comprehensive diagnosis following the same structure as above.
Note: No image available, so rely on symptom description only.
Increase confidence range by asking for more info if needed."""


async def detect_disease(
    description: str,
    crop_type: Optional[str] = None,
    location: Optional[Dict[str, Any]] = None,
    season: Optional[str] = None,
    growth_stage: Optional[str] = None,
    image_urls: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Main disease detection entry point.
    
    Returns structured diagnosis dict with findings, recommendations, severity.
    """
    loc_str = _format_location(location)
    crop = crop_type or "unknown crop"
    season_str = season or "unknown season"
    stage = growth_stage or "unknown stage"

    # ── Vision analysis (if images provided) ──────────────────────────────────
    if image_urls:
        prompt = VISION_DISEASE_PROMPT.format(
            crop_type=crop,
            location=loc_str,
            season=season_str,
            growth_stage=stage,
            description=description,
        )
        try:
            raw = await vision_completion(
                text_prompt=prompt,
                image_urls=image_urls,
                system_override=DISEASE_SYSTEM_PROMPT,
            )
            return _parse_llm_response(raw, has_image=True)
        except Exception as e:
            logger.warning("Vision analysis failed, falling back to text: %s", e)

    # ── Text-only analysis ────────────────────────────────────────────────────
    prompt = TEXT_DISEASE_PROMPT.format(
        crop_type=crop,
        location=loc_str,
        season=season_str,
        growth_stage=stage,
        description=description,
    )
    raw = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model_alias="reasoning",
        system_override=DISEASE_SYSTEM_PROMPT,
        temperature=0.2,
        max_tokens=2000,
    )
    return _parse_llm_response(raw, has_image=False)


def _parse_llm_response(raw: str, has_image: bool) -> Dict[str, Any]:
    """Parse LLM output into structured agent result."""
    import json, re

    # Try JSON parse first
    json_match = re.search(r'\{[\s\S]+\}', raw)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return _normalize_diagnosis(data, has_image)
        except json.JSONDecodeError:
            pass

    # Fallback: extract key sections from text
    return {
        "primary_diagnosis": _extract_section(raw, "PRIMARY DIAGNOSIS", "General crop issue detected"),
        "symptoms_observed": _extract_section(raw, "SYMPTOMS OBSERVED", "See description"),
        "severity": _extract_severity(raw),
        "confidence": 0.65 if has_image else 0.50,
        "differential_diagnoses": [],
        "immediate_actions": _extract_list(raw, "IMMEDIATE ACTIONS"),
        "treatment_protocol": _extract_section(raw, "TREATMENT PROTOCOL", "Consult local agronomist"),
        "organic_alternatives": _extract_list(raw, "ORGANIC ALTERNATIVES"),
        "preventive_measures": _extract_list(raw, "PREVENTIVE MEASURES"),
        "follow_up": _extract_section(raw, "FOLLOW-UP", "Monitor in 5-7 days"),
        "warnings": _extract_list(raw, "WARNINGS"),
        "raw_analysis": raw,
        "analysis_source": "vision" if has_image else "text",
    }


def _normalize_diagnosis(data: Dict, has_image: bool) -> Dict[str, Any]:
    """Normalize LLM JSON into standard schema."""
    return {
        "primary_diagnosis": data.get("primary_diagnosis") or data.get("PRIMARY DIAGNOSIS", "Unknown"),
        "symptoms_observed": data.get("symptoms_observed") or data.get("SYMPTOMS OBSERVED", ""),
        "severity": data.get("severity") or data.get("SEVERITY", "medium"),
        "confidence": float(data.get("confidence", 70)) / 100 if float(data.get("confidence", 0.7)) > 1 else float(data.get("confidence", 0.7)),
        "differential_diagnoses": data.get("differential_diagnoses") or data.get("DIFFERENTIAL DIAGNOSES", []),
        "immediate_actions": _ensure_list(data.get("immediate_actions") or data.get("IMMEDIATE ACTIONS", [])),
        "treatment_protocol": data.get("treatment_protocol") or data.get("TREATMENT PROTOCOL", ""),
        "organic_alternatives": _ensure_list(data.get("organic_alternatives") or data.get("ORGANIC ALTERNATIVES", [])),
        "preventive_measures": _ensure_list(data.get("preventive_measures") or data.get("PREVENTIVE MEASURES", [])),
        "follow_up": data.get("follow_up") or data.get("FOLLOW-UP", "Monitor in 5-7 days"),
        "warnings": _ensure_list(data.get("warnings") or data.get("WARNINGS", [])),
        "analysis_source": "vision" if has_image else "text",
    }


def _ensure_list(val: Any) -> List[str]:
    if isinstance(val, list):
        return [str(v) for v in val]
    if isinstance(val, str):
        return [val] if val else []
    return []


def _extract_section(text: str, heading: str, default: str) -> str:
    import re
    pattern = rf"{heading}[:\-]?\s*(.+?)(?=\n[A-Z]|\Z)"
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else default


def _extract_list(text: str, heading: str) -> List[str]:
    import re
    pattern = rf"{heading}[:\-]?\s*([\s\S]+?)(?=\n[A-Z0-9]|\Z)"
    m = re.search(pattern, text, re.IGNORECASE)
    if not m:
        return []
    block = m.group(1)
    items = re.findall(r"[-•*\d]+\.\s*(.+)", block)
    return [i.strip() for i in items if i.strip()]


def _extract_severity(text: str) -> str:
    import re
    m = re.search(r"severity[:\s]+(low|medium|high|critical)", text, re.IGNORECASE)
    return m.group(1).lower() if m else "medium"


def _format_location(loc: Optional[Dict]) -> str:
    if not loc:
        return "India"
    parts = [loc.get("district"), loc.get("state"), loc.get("country", "India")]
    return ", ".join(p for p in parts if p)
