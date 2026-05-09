from __future__ import annotations
from typing import Any, Dict, List
from agents.crop.image_analysis.tools import extract_image_signals

def analyze_images(
    image_inputs: List[Dict[str, Any]],
    crop_type: str | None = None,
    location: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    signals = extract_image_signals(image_inputs)

    findings = []
    recommendations = []
    warnings = []

    if "possible_leaf_issue" in signals:
        findings.append({
            "label": "leaf_abnormality",
            "severity": "medium",
            "confidence": 0.81,
            "description": f"The image hints at a leaf issue on {crop_type or 'the crop'}."
        })
        recommendations.extend([
            "Inspect the underside of the leaf for pests.",
            "Compare several leaves from the same field to confirm the pattern.",
        ])
        warnings.append("Do not spray pesticides until the disease is confirmed.")

    if "water_stress" in signals:
        findings.append({
            "label": "water_stress",
            "severity": "medium",
            "confidence": 0.77,
            "description": "The image suggests possible drought or irregular irrigation stress."
        })
        recommendations.append("Check soil moisture at root depth before applying more water.")

    if not findings:
        findings.append({
            "label": "no_clear_issue",
            "severity": "low",
            "confidence": 0.58,
            "description": "No strong visual issue detected from the filename-based starter analysis."
        })
        recommendations.append("Upload a sharper close-up photo in daylight for a better diagnosis.")

    return {
        "findings": findings,
        "recommendations": recommendations,
        "warnings": warnings,
        "summary": "Image analysis completed using the starter offline heuristic engine.",
        "meta": {
            "crop_type": crop_type,
            "location": location,
            "signals": signals,
        },
    }
