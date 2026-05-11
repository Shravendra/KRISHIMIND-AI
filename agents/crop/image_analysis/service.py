"""Multi-image crop analysis service.

Accepts up to 4 base64-encoded images and returns a consolidated
disease / health assessment using the vision LLM.
"""

import json
import re
from typing import List, Optional, Dict, Any

from shared.llm.client import LLMClient
from shared.utils.logging import get_logger

logger = get_logger("agents.image_analysis")
_llm = LLMClient()

ANALYSIS_SYSTEM_PROMPT = """You are an expert agricultural plant pathologist and agronomist with 20+ years of experience diagnosing crop diseases across India.

Analyse the provided plant/crop image(s) and return ONLY a JSON object.

JSON format:
{
  "overall_health": "healthy|stressed|diseased|critical",
  "health_score": 0-100,
  "observations": [
    {
      "area": "leaves|stem|roots|fruit|whole_plant",
      "observation": "<what you see>",
      "significance": "normal|concern|serious"
    }
  ],
  "diseases_detected": [
    {
      "name": "<common name>",
      "scientific_name": "<scientific name>",
      "confidence": 0.0-1.0,
      "severity": "mild|moderate|severe|critical",
      "affected_area_percent": 0-100,
      "spread_risk": "low|medium|high"
    }
  ],
  "pests_detected": [
    {
      "name": "<pest name>",
      "confidence": 0.0-1.0,
      "damage_type": "<description>"
    }
  ],
  "nutrient_deficiencies": [
    {
      "nutrient": "<nutrient name>",
      "confidence": 0.0-1.0,
      "symptoms": "<visible symptoms>"
    }
  ],
  "immediate_actions": ["<action 1>", ...],
  "treatment_plan": {
    "chemical": ["<product and dose>", ...],
    "organic": ["<organic remedy>", ...],
    "cultural": ["<cultural practice>", ...]
  },
  "prevention": ["<prevention tip>", ...],
  "estimated_yield_impact": "<e.g. 20-30% loss if untreated>",
  "urgency": "low|medium|high|critical",
  "summary": "<2-3 sentence plain English summary>"
}

Be specific about Indian market products where possible. If the image quality is poor, note it but still provide your best assessment."""


async def analyze_images(
    images: List[str],
    crop_type: Optional[str] = None,
    context: Optional[str] = None,
) -> Dict[str, Any]:
    """Analyse one or more base64-encoded plant images.

    Args:
        images: List of base64-encoded image strings (JPEG or PNG).
        crop_type: Optional crop name hint (e.g. "tomato").
        context: Any additional textual context from the user.

    Returns:
        Parsed analysis dict.
    """
    if not images:
        return {"error": "No images provided"}

    # Build the vision prompt
    user_parts: List[Dict] = []

    if crop_type or context:
        intro_parts = []
        if crop_type:
            intro_parts.append(f"Crop type: {crop_type}")
        if context:
            intro_parts.append(f"Additional context: {context}")
        user_parts.append({"type": "text", "text": "\n".join(intro_parts)})

    user_parts.append({
        "type": "text",
        "text": f"Please analyse {'this image' if len(images) == 1 else f'these {len(images)} images'} of the crop:"
    })

    for i, img_b64 in enumerate(images[:4]):  # max 4 images
        # Detect media type from base64 header or assume JPEG
        if img_b64.startswith("/9j/") or img_b64.startswith("iVBORw0KGgo"):
            media_type = "image/png" if img_b64.startswith("iVBORw0KGgo") else "image/jpeg"
        else:
            media_type = "image/jpeg"

        user_parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:{media_type};base64,{img_b64}"},
        })

    try:
        raw = await _llm.vision_completion(
            messages=[{"role": "user", "content": user_parts}],
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
            max_tokens=1200,
        )

        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        result = json.loads(cleaned)

        logger.info(
            "image_analysis_complete",
            extra={
                "image_count": len(images),
                "health": result.get("overall_health"),
                "urgency": result.get("urgency"),
                "diseases_count": len(result.get("diseases_detected", [])),
            },
        )
        return result

    except json.JSONDecodeError:
        # Return the raw text wrapped in a minimal structure
        logger.warning("image_analysis_json_parse_error")
        return {
            "overall_health": "unknown",
            "health_score": None,
            "summary": raw[:500] if raw else "Analysis could not be parsed.",
            "diseases_detected": [],
            "immediate_actions": ["Please consult a local agricultural expert."],
            "urgency": "medium",
        }
    except Exception as exc:
        logger.error("image_analysis_error", extra={"error": str(exc)})
        return {
            "overall_health": "unknown",
            "health_score": None,
            "summary": "Image analysis failed. Please try again.",
            "error": str(exc),
            "diseases_detected": [],
            "immediate_actions": [],
            "urgency": "low",
        }
