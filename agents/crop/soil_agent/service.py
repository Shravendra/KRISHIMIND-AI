"""
agents/crop/soil_agent/service.py
──────────────────────────────────
Soil health analysis and recommendation agent.
Analyzes pH, NPK, organic matter, texture, and irrigation suitability.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from shared.llm.client import chat_completion
from shared.utils.logging import get_logger

logger = get_logger(__name__)

SOIL_SYSTEM_PROMPT = """You are a certified soil scientist and agronomist with expertise in Indian soils.
You specialize in:
- Soil classification (alluvial, black cotton, red laterite, sandy, clay loam)
- pH analysis and amendment recommendations
- NPK (Nitrogen, Phosphorus, Potassium) status and fertilizer calculations
- Micro-nutrient deficiencies (Fe, Zn, Cu, Mn, B, Mo)
- Organic carbon and matter improvements
- Water retention and drainage optimization
- Soil salinity and sodicity management
- Bio-fertilizer recommendations (Rhizobium, PSB, KMB)

For each recommendation:
- Specify exact quantity in kg/acre or bags/acre
- Name specific products available in Indian market
- Include timing relative to crop cycle
- Suggest both organic and inorganic options
- Warn about over-application risks

Be farmer-friendly: use simple terms, give local product names, 
and prioritize cost-effective solutions for small/medium farmers."""

SOIL_ANALYSIS_PROMPT = """Analyze the following soil test report and provide comprehensive recommendations:

SOIL TEST RESULTS:
pH: {ph}
Nitrogen (N): {nitrogen} kg/ha
Phosphorus (P): {phosphorus} kg/ha  
Potassium (K): {potassium} kg/ha
Organic Carbon: {organic_carbon}%
EC (Salinity): {ec} dS/m
Soil Texture: {texture}
Zinc: {zinc} ppm
Iron: {iron} ppm
Boron: {boron} ppm

FARM CONTEXT:
Crop: {crop}
Season: {season}
Location: {location}
Irrigation: {irrigation}
Previous crop: {previous_crop}

Provide detailed recommendations as JSON with:
1. soil_health_score (0-100)
2. ph_status: (acidic/neutral/alkaline) with amendment needed
3. npk_status: status of each + deficiency level
4. micronutrient_issues: list of deficient micronutrients
5. organic_matter_status: poor/fair/good/excellent
6. salinity_status: normal/mild/moderate/severe
7. recommended_amendments: list with product, quantity, timing, cost
8. fertilizer_schedule: NPK application plan for the crop
9. organic_recommendations: compost/FYM/bio-fertilizers
10. soil_improvement_practices: long-term improvements
11. irrigation_advice: based on texture and EC
12. warnings: any urgent concerns
13. summary: 3-4 sentence farmer-friendly summary"""

BASIC_SOIL_PROMPT = """A farmer describes their soil situation:

Crop: {crop}
Location: {location}
Season: {season}
Soil description: {description}
Observed symptoms: {symptoms}

Without a formal soil test, provide:
1. Likely soil type for this region
2. Common deficiencies in this crop/region combination
3. Basic soil health package recommendation
4. How to get a proper soil test done (Soil Health Card scheme)
5. Immediate actions they can take
6. Budget-friendly organic soil improvement plan

Format as structured JSON."""


async def analyze_soil(
    description: str,
    crop: Optional[str] = None,
    season: Optional[str] = None,
    location: Optional[Dict[str, Any]] = None,
    soil_test_data: Optional[Dict[str, Any]] = None,
    previous_crop: Optional[str] = None,
    irrigation_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze soil health and provide amendment recommendations.
    """
    loc_str = _format_location(location)
    crop_str = crop or "general crops"

    if soil_test_data:
        # Full soil test analysis
        prompt = SOIL_ANALYSIS_PROMPT.format(
            ph=soil_test_data.get("ph", "not available"),
            nitrogen=soil_test_data.get("nitrogen", "not available"),
            phosphorus=soil_test_data.get("phosphorus", "not available"),
            potassium=soil_test_data.get("potassium", "not available"),
            organic_carbon=soil_test_data.get("organic_carbon", "not available"),
            ec=soil_test_data.get("ec", "not available"),
            texture=soil_test_data.get("texture", "not available"),
            zinc=soil_test_data.get("zinc", "not available"),
            iron=soil_test_data.get("iron", "not available"),
            boron=soil_test_data.get("boron", "not available"),
            crop=crop_str,
            season=season or "kharif",
            location=loc_str,
            irrigation=irrigation_type or "not specified",
            previous_crop=previous_crop or "not specified",
        )
        model = "reasoning"
    else:
        # Basic analysis from description
        symptoms = description
        prompt = BASIC_SOIL_PROMPT.format(
            crop=crop_str,
            location=loc_str,
            season=season or "kharif",
            description=description,
            symptoms=symptoms,
        )
        model = "cheap"

    raw = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model_alias=model,
        system_override=SOIL_SYSTEM_PROMPT,
        temperature=0.2,
        max_tokens=2000,
    )

    return _parse_soil_response(raw, has_test_data=bool(soil_test_data))


def _parse_soil_response(raw: str, has_test_data: bool) -> Dict[str, Any]:
    import json, re

    json_match = re.search(r'\{[\s\S]+\}', raw)
    if json_match:
        try:
            data = json.loads(json_match.group())
            data["raw_analysis"] = raw
            data["has_soil_test"] = has_test_data
            return data
        except json.JSONDecodeError:
            pass

    return {
        "soil_health_score": 60,
        "summary": raw[:500] if raw else "Soil analysis completed.",
        "recommended_amendments": [],
        "fertilizer_schedule": [],
        "organic_recommendations": [],
        "warnings": [],
        "raw_analysis": raw,
        "has_soil_test": has_test_data,
    }


def _format_location(loc: Optional[Dict]) -> str:
    if not loc:
        return "India"
    parts = [loc.get("district"), loc.get("state"), loc.get("country", "India")]
    return ", ".join(p for p in parts if p)
