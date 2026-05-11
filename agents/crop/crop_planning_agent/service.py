"""
agents/crop/crop_planning_agent/service.py
───────────────────────────────────────────
Crop selection, rotation planning, and sowing calendar agent.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from shared.llm.client import chat_completion
from shared.utils.logging import get_logger

logger = get_logger(__name__)

CROP_PLANNING_SYSTEM = """You are an expert agronomist specializing in crop planning, rotation, 
and precision agriculture for Indian farming systems.

Your knowledge covers:
- 500+ crop varieties suited for Indian agro-climatic zones
- Crop rotation benefits (disease break, nitrogen fixation, weed suppression)
- Intercropping systems (Sugarcane+Soybean, Maize+Black gram, etc.)
- Agro-climatic zone mapping (18 zones in India)
- Market-linked crop planning (price trends, demand forecast)
- Climate-resilient varieties (drought, flood, heat tolerant)
- Organic certification-compatible crop sequences
- Government scheme eligibility (PM-KISAN, PMFBY crop list)
- Input cost vs revenue projections

Consider always:
- Farmer's water availability
- Labor availability and mechanization level
- Market access (proximity to mandis, cold chain)
- Soil health impact of crop sequence
- Risk diversification (mono vs mixed cropping)"""

CROP_PLANNING_PROMPT = """Help plan crops for this farmer:

FARMER PROFILE:
Location: {location}
Land Size: {land_size} acres
Soil Type: {soil_type}
Water Source: {water_source}
Current/Last Crop: {current_crop}
Season Planning For: {season}
Budget: {budget}
Market Access: {market_access}

CONSTRAINTS/PREFERENCES:
{additional_info}

Provide a comprehensive crop plan as JSON:
{{
  "top_3_recommended_crops": [
    {{
      "crop": "",
      "variety": "",
      "reason": "",
      "expected_yield_qtl_per_acre": 0,
      "expected_revenue_inr_per_acre": 0,
      "input_cost_inr_per_acre": 0,
      "net_profit_inr_per_acre": 0,
      "water_requirement": "low/medium/high",
      "risk_level": "low/medium/high",
      "market_demand": "good/average/poor",
      "government_schemes": []
    }}
  ],
  "crop_rotation_plan": {{
    "kharif": "",
    "rabi": "",
    "zaid": "",
    "2_year_plan": "",
    "benefits": []
  }},
  "intercropping_options": [
    {{
      "main_crop": "",
      "intercrop": "",
      "spacing": "",
      "benefit": "",
      "additional_income_inr_per_acre": 0
    }}
  ],
  "sowing_calendar": [
    {{
      "crop": "",
      "land_area_acres": 0,
      "sowing_window": "",
      "harvest_window": "",
      "key_milestones": []
    }}
  ],
  "risk_mitigation": [],
  "organic_transition_advice": "",
  "government_schemes": [],
  "summary": "practical 3-4 sentence guidance"
}}"""


async def plan_crops(
    location: Optional[Dict[str, Any]] = None,
    land_size_acres: Optional[float] = None,
    current_crop: Optional[str] = None,
    season: Optional[str] = None,
    soil_type: Optional[str] = None,
    water_source: Optional[str] = None,
    budget_inr: Optional[float] = None,
    market_access: Optional[str] = None,
    description: str = "",
) -> Dict[str, Any]:
    """Generate crop planning recommendations."""
    loc_str = _format_location(location)

    prompt = CROP_PLANNING_PROMPT.format(
        location=loc_str,
        land_size=land_size_acres or "not specified",
        soil_type=soil_type or "not specified",
        water_source=water_source or "rainfed",
        current_crop=current_crop or "not specified",
        season=season or "next season",
        budget=f"₹{budget_inr:,.0f}" if budget_inr else "not specified",
        market_access=market_access or "local mandi",
        additional_info=description or "No additional constraints specified",
    )

    raw = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model_alias="reasoning",
        system_override=CROP_PLANNING_SYSTEM,
        temperature=0.3,
        max_tokens=2500,
    )

    return _parse_crop_plan(raw)


def _parse_crop_plan(raw: str) -> Dict[str, Any]:
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
        "summary": raw[:500] if raw else "Crop plan generated.",
        "top_3_recommended_crops": [],
        "crop_rotation_plan": {},
        "sowing_calendar": [],
        "raw_analysis": raw,
    }


def _format_location(loc: Optional[Dict]) -> str:
    if not loc:
        return "India"
    parts = [loc.get("district"), loc.get("state"), loc.get("country", "India")]
    return ", ".join(p for p in parts if p)
