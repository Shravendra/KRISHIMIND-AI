"""
agents/crop/weather_agent/service.py
─────────────────────────────────────
Hyper-local weather risk assessment and advisory agent.
Integrates OpenWeatherMap API + LLM analysis for farm-specific guidance.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx
from shared.llm.client import chat_completion
from shared.utils.logging import get_logger

logger = get_logger(__name__)
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

WEATHER_SYSTEM_PROMPT = """You are an agricultural meteorologist and weather risk advisor.
You specialize in translating weather data into actionable farm management advice.

Your expertise includes:
- Drought stress management and irrigation scheduling
- Frost and cold wave protection strategies  
- Heat stress mitigation for crops and livestock
- Flood and waterlogging response protocols
- Disease-favorable weather early warning (humidity + temperature combos)
- Optimal spray windows (wind speed, temperature, humidity)
- Harvest weather windows
- Cyclone and storm preparedness

For each weather risk:
1. Explain the risk in simple farmer language
2. Rate severity: low | medium | high | critical
3. Give specific actions with timing
4. Estimate economic impact if action not taken
5. Provide crop-specific guidance
6. Suggest insurance/documentation advice for extreme events

Use Indian agricultural context (cropping calendar, local risk patterns)."""

WEATHER_ADVISORY_PROMPT = """Weather Risk Analysis for Farmer:

LOCATION: {location}
CROP: {crop}
GROWTH STAGE: {growth_stage}
SEASON: {season}

CURRENT WEATHER DATA:
Temperature: {temp}°C (feels like {feels_like}°C)
Humidity: {humidity}%
Wind Speed: {wind_speed} m/s
Rainfall: {rainfall} mm (last 24h)
Weather Condition: {condition}
Pressure: {pressure} hPa

7-DAY FORECAST SUMMARY:
{forecast_summary}

FARMER QUERY: {query}

Provide a comprehensive weather-based farm advisory as JSON:
{{
  "overall_risk_level": "low/medium/high/critical",
  "primary_risks": [
    {{
      "risk_type": "",
      "severity": "low/medium/high/critical", 
      "probability": 0-100,
      "description": "",
      "affected_crops": [],
      "economic_impact": ""
    }}
  ],
  "immediate_actions": [
    {{
      "action": "",
      "timing": "",
      "reason": "",
      "priority": "urgent/important/optional"
    }}
  ],
  "irrigation_advice": {{
    "status": "deficit/adequate/excess",
    "recommendation": "",
    "schedule": ""
  }},
  "spray_window": {{
    "suitable_today": true/false,
    "best_time": "",
    "conditions": ""
  }},
  "disease_risk_from_weather": {{
    "risk_level": "",
    "diseases_likely": [],
    "preventive_spray": ""
  }},
  "harvest_window": {{
    "suitable": true/false,
    "recommendation": "",
    "avoid_dates": []
  }},
  "alerts": [],
  "7_day_farm_plan": "",
  "summary": "2-3 sentence practical summary"
}}"""

WEATHER_FALLBACK_PROMPT = """A farmer in {location} growing {crop} asks about weather risks:

Query: {query}
Season: {season}
Growth stage: {growth_stage}

Without real-time weather data, provide:
1. Typical weather risks for this region and season
2. Common weather-related crop problems to watch for
3. General preventive measures
4. How to set up weather monitoring on their farm
5. When to seek updated weather advisory

Be practical and specific to Indian farming context."""


async def assess_weather_risk(
    query: str = "",
    crop: Optional[str] = None,
    growth_stage: Optional[str] = None,
    season: Optional[str] = None,
    location: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assess weather risks and provide farm advisory."""
    loc_str = _format_location(location)
    crop_str = crop or "mixed crops"

    # Try to fetch real weather data
    weather_data = None
    if location and WEATHER_API_KEY:
        weather_data = await _fetch_weather(location)

    if weather_data:
        prompt = WEATHER_ADVISORY_PROMPT.format(
            location=loc_str,
            crop=crop_str,
            growth_stage=growth_stage or "vegetative",
            season=season or "kharif",
            temp=weather_data.get("temp", "N/A"),
            feels_like=weather_data.get("feels_like", "N/A"),
            humidity=weather_data.get("humidity", "N/A"),
            wind_speed=weather_data.get("wind_speed", "N/A"),
            rainfall=weather_data.get("rainfall", 0),
            condition=weather_data.get("condition", "N/A"),
            pressure=weather_data.get("pressure", "N/A"),
            forecast_summary=weather_data.get("forecast_summary", "Not available"),
            query=query or "What weather risks should I watch for?",
        )
    else:
        prompt = WEATHER_FALLBACK_PROMPT.format(
            location=loc_str,
            crop=crop_str,
            query=query or "General weather advisory needed",
            season=season or "kharif",
            growth_stage=growth_stage or "vegetative",
        )

    raw = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model_alias="cheap",
        system_override=WEATHER_SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=2000,
    )

    result = _parse_weather_response(raw)
    if weather_data:
        result["live_weather"] = weather_data
    result["location"] = loc_str
    return result


async def _fetch_weather(location: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fetch weather from OpenWeatherMap API."""
    try:
        lat = location.get("lat")
        lon = location.get("lon")
        if not (lat and lon):
            return None

        async with httpx.AsyncClient(timeout=10) as client:
            # Current weather
            current_resp = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"lat": lat, "lon": lon, "appid": WEATHER_API_KEY, "units": "metric"},
            )
            if current_resp.status_code != 200:
                return None

            current = current_resp.json()

            # 5-day forecast
            forecast_resp = await client.get(
                "https://api.openweathermap.org/data/2.5/forecast",
                params={"lat": lat, "lon": lon, "appid": WEATHER_API_KEY, "units": "metric"},
            )
            forecast_data = forecast_resp.json() if forecast_resp.status_code == 200 else {}

        forecast_summary = _summarize_forecast(forecast_data)

        return {
            "temp": current["main"]["temp"],
            "feels_like": current["main"]["feels_like"],
            "humidity": current["main"]["humidity"],
            "wind_speed": current["wind"]["speed"],
            "pressure": current["main"]["pressure"],
            "condition": current["weather"][0]["description"],
            "rainfall": current.get("rain", {}).get("1h", 0),
            "forecast_summary": forecast_summary,
        }
    except Exception as e:
        logger.warning("Weather fetch failed: %s", e)
        return None


def _summarize_forecast(forecast_data: Dict) -> str:
    """Summarize 5-day forecast into text."""
    if not forecast_data.get("list"):
        return "Forecast unavailable"

    items = forecast_data["list"][:8]  # 24 hours
    temps = [i["main"]["temp"] for i in items]
    conditions = [i["weather"][0]["description"] for i in items]
    rain = [i.get("rain", {}).get("3h", 0) for i in items]

    return (
        f"Next 24h: Temps {min(temps):.0f}-{max(temps):.0f}°C, "
        f"Conditions: {', '.join(set(conditions[:3]))}, "
        f"Expected rainfall: {sum(rain):.1f}mm"
    )


def _parse_weather_response(raw: str) -> Dict[str, Any]:
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
        "overall_risk_level": "medium",
        "summary": raw[:400] if raw else "Weather assessment complete.",
        "immediate_actions": [],
        "alerts": [],
        "raw_analysis": raw,
    }


def _format_location(loc: Optional[Dict]) -> str:
    if not loc:
        return "India"
    parts = [loc.get("district"), loc.get("state"), loc.get("country", "India")]
    return ", ".join(p for p in parts if p)
