"""
agents/crop/fertilizer_agent/service.py
────────────────────────────────────────
Fertilizer optimization agent.
Calculates NPK requirements, schedules applications, and recommends products.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from shared.llm.client import chat_completion
from shared.utils.logging import get_logger

logger = get_logger(__name__)

FERTILIZER_SYSTEM_PROMPT = """You are a certified fertilizer management expert and crop nutrition specialist.
You have comprehensive knowledge of:

FERTILIZER PRODUCTS (India):
- Urea (46% N), DAP (18-46-0), MOP (0-0-60), NPK complexes (10-26-26, 12-32-16, 20-20-0)
- SSP (16% P), TSP (46% P), Ammonium Sulphate (21% N + 24% S)
- Micronutrient mixtures: Zinc Sulphate, Ferrous Sulphate, Borax
- Bio-fertilizers: Rhizobium, PSB, KMB, Azotobacter, VAM
- Organic: FYM, vermicompost, neem cake, bone meal, green manure

CALCULATION PRINCIPLES:
- Yield-based nutrient requirement
- Soil test based dose correction
- Split application scheduling
- Fertigation through drip/sprinkler
- Foliar spray for micronutrients

CONSTRAINTS:
- Government subsidy implications
- Cost-benefit analysis
- Environmental impact (leaching, volatilization)
- Safe handling and storage
- Mixing compatibility

Always calculate exact kg/acre, mention government MRP, and flag subsidy eligibility."""

FERTILIZER_PROMPT = """Calculate the complete fertilizer management plan for:

CROP DETAILS:
Crop: {crop}
Variety: {variety}
Season: {season}
Growth Stage: {growth_stage}
Target Yield: {target_yield} quintals/acre
Land Size: {land_size} acres

SOIL STATUS (if available):
pH: {ph}
N status: {n_status}
P status: {p_status}
K status: {k_status}
Organic Carbon: {oc}%
Previous crop: {previous_crop}

LOCATION & CLIMATE:
Location: {location}
Irrigation available: {irrigation}

Provide a complete fertilizer plan as JSON:
{{
  "total_npk_requirement": {{"N": kg_per_acre, "P": kg_per_acre, "K": kg_per_acre}},
  "soil_correction": {{"adjustments": [], "reasoning": ""}},
  "fertilizer_schedule": [
    {{
      "stage": "basal/top-dress-1/top-dress-2/etc",
      "timing": "days after sowing or growth stage",
      "products": [
        {{
          "name": "product name",
          "quantity_kg_per_acre": number,
          "method": "broadcasting/drilling/fertigation/foliar",
          "cost_per_acre_inr": number,
          "notes": ""
        }}
      ]
    }}
  ],
  "micronutrient_package": [
    {{"nutrient": "", "product": "", "dose": "", "method": "", "timing": ""}}
  ],
  "bio_fertilizer_package": [
    {{"name": "", "dose": "", "method": "", "benefit": ""}}
  ],
  "organic_supplement": {{"product": "", "quantity_per_acre": "", "timing": "", "benefit": ""}},
  "total_fertilizer_cost_inr_per_acre": number,
  "expected_yield_increase_percent": number,
  "important_tips": [],
  "dos_and_donts": [],
  "warnings": [],
  "summary": "3-4 sentence practical summary"
}}"""


async def optimize_fertilizer(
    crop: Optional[str] = None,
    variety: Optional[str] = None,
    season: Optional[str] = None,
    growth_stage: Optional[str] = None,
    land_size_acres: Optional[float] = None,
    target_yield: Optional[float] = None,
    soil_data: Optional[Dict[str, Any]] = None,
    location: Optional[Dict[str, Any]] = None,
    previous_crop: Optional[str] = None,
    irrigation_type: Optional[str] = None,
    description: str = "",
) -> Dict[str, Any]:
    """Generate optimized fertilizer management plan."""

    soil = soil_data or {}
    loc_str = _format_location(location)

    prompt = FERTILIZER_PROMPT.format(
        crop=crop or "mixed crops",
        variety=variety or "common variety",
        season=season or "kharif",
        growth_stage=growth_stage or "pre-sowing",
        target_yield=target_yield or "average",
        land_size=land_size_acres or 1,
        ph=soil.get("ph", "not tested"),
        n_status=soil.get("n_status", "unknown"),
        p_status=soil.get("p_status", "unknown"),
        k_status=soil.get("k_status", "unknown"),
        oc=soil.get("organic_carbon", "unknown"),
        previous_crop=previous_crop or "not specified",
        location=loc_str,
        irrigation=irrigation_type or "rainfed",
    )

    if description:
        prompt += f"\n\nAdditional farmer context: {description}"

    raw = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model_alias="reasoning",
        system_override=FERTILIZER_SYSTEM_PROMPT,
        temperature=0.2,
        max_tokens=2500,
    )

    return _parse_fertilizer_response(raw)


def _parse_fertilizer_response(raw: str) -> Dict[str, Any]:
    import json, re

    json_match = re.search(r'\{[\s\S]+\}', raw)
    if json_match:
        try:
            data = json.loads(json_match.group())
            data["raw_analysis"] = raw
            return data
        except json.JSONDecodeError:
            pass

    return {
        "summary": raw[:400] if raw else "Fertilizer plan generated.",
        "fertilizer_schedule": [],
        "warnings": [],
        "raw_analysis": raw,
    }


def _format_location(loc: Optional[Dict]) -> str:
    if not loc:
        return "India"
    parts = [loc.get("district"), loc.get("state"), loc.get("country", "India")]
    return ", ".join(p for p in parts if p)
