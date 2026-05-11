"""
agents/market/price_forecast_agent/service.py
──────────────────────────────────────────────
Crop commodity price forecasting and market advisory agent.
Combines market intelligence with LLM analysis for selling strategy.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from shared.llm.client import chat_completion
from shared.utils.logging import get_logger

logger = get_logger(__name__)

MARKET_SYSTEM_PROMPT = """You are an agricultural market intelligence analyst specializing in Indian 
commodity markets and farm gate price optimization.

Your expertise covers:
- APMC mandi price trends (all major mandis)
- MSP (Minimum Support Price) for notified crops
- Export/import policies affecting farm prices
- Seasonal price patterns and cycles
- Market arrivals and supply-demand dynamics
- e-NAM (National Agriculture Market) platform
- Forward contracts and futures (NCDEX, MCX)
- Direct farmer-buyer linkages (FPOs, contract farming)
- Storage decisions (warehouse receipt financing)
- Value addition opportunities

When advising:
1. Give specific price ranges (₹/quintal) for the crop and region
2. Identify best selling window (month/fortnight)
3. Compare nearby mandis
4. Advise on hold vs sell decision
5. Mention MSP and procurement centers
6. Suggest value addition to increase price realization
7. Flag any policy changes affecting prices
8. Include risk factors (glut, export ban, etc.)"""

MARKET_ADVISORY_PROMPT = """Market Price Analysis and Selling Strategy:

CROP DETAILS:
Crop: {crop}
Variety: {variety}
Quality Grade: {quality}
Quantity: {quantity} quintals
Expected Harvest: {harvest_date}

FARMER LOCATION:
Location: {location}
Nearest Mandis: {nearest_mandis}

CURRENT SITUATION:
Current price query: {query}
Storage available: {storage} months
Financial urgency: {urgency}

Provide comprehensive market advisory as JSON:
{{
  "current_market_overview": {{
    "estimated_current_price_inr_per_quintal": 0,
    "price_range": {{"min": 0, "max": 0}},
    "msp_if_applicable": 0,
    "market_trend": "rising/stable/falling",
    "trend_confidence": 0-100
  }},
  "price_forecast": [
    {{"month": "", "estimated_price": 0, "reasoning": ""}}
  ],
  "selling_strategy": {{
    "recommendation": "sell_now/hold/partial_sell",
    "best_selling_window": "",
    "expected_price_at_best_window": 0,
    "potential_gain_per_quintal": 0,
    "risk_of_holding": "low/medium/high",
    "strategy_explanation": ""
  }},
  "nearby_markets": [
    {{"mandi": "", "distance_km": 0, "current_price": 0, "advantage": ""}}
  ],
  "alternative_channels": [
    {{"channel": "FPO/e-NAM/direct/contract", "price_advantage": "", "how_to_access": ""}}
  ],
  "value_addition_options": [
    {{"option": "", "investment_inr": 0, "price_premium_percent": 0}}
  ],
  "storage_advice": {{
    "recommended_duration": "",
    "storage_type": "",
    "warehouse_receipt_available": true/false,
    "cost_per_quintal_per_month": 0
  }},
  "government_support": [],
  "market_risks": [],
  "summary": "practical 3-4 sentence advice"
}}"""


async def analyze_market(
    crop: Optional[str] = None,
    variety: Optional[str] = None,
    quantity_quintals: Optional[float] = None,
    quality_grade: Optional[str] = None,
    harvest_date: Optional[str] = None,
    location: Optional[Dict[str, Any]] = None,
    storage_months: Optional[int] = None,
    financial_urgency: str = "medium",
    query: str = "",
) -> Dict[str, Any]:
    """Analyze market conditions and provide selling strategy."""
    loc_str = _format_location(location)

    prompt = MARKET_ADVISORY_PROMPT.format(
        crop=crop or "general commodity",
        variety=variety or "standard variety",
        quality=quality_grade or "FAQ (Fair Average Quality)",
        quantity=quantity_quintals or "not specified",
        harvest_date=harvest_date or "upcoming harvest",
        location=loc_str,
        nearest_mandis=f"mandis near {loc_str}",
        query=query or "What is the best time and place to sell?",
        storage=storage_months or 0,
        urgency=financial_urgency,
    )

    raw = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model_alias="reasoning",
        system_override=MARKET_SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=2000,
    )

    return _parse_market_response(raw)


def _parse_market_response(raw: str) -> Dict[str, Any]:
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
        "summary": raw[:400] if raw else "Market analysis complete.",
        "selling_strategy": {"recommendation": "consult_local_mandi"},
        "market_risks": [],
        "raw_analysis": raw,
    }


def _format_location(loc: Optional[Dict]) -> str:
    if not loc:
        return "India"
    parts = [loc.get("district"), loc.get("state"), loc.get("country", "India")]
    return ", ".join(p for p in parts if p)
