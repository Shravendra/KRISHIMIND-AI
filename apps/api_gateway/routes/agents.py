"""Agent management routes — list available agents, invoke image analysis."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import base64

from shared.auth.jwt import get_current_user
from shared.constants.app import ALL_AGENTS
from shared.utils.logging import get_logger
from agents.crop.image_analysis.service import analyze_images

logger = get_logger("api.agents")
router = APIRouter(prefix="/agents", tags=["agents"])


AGENT_META = {
    "disease_detection":        {"name": "Disease Detection",        "icon": "🔬", "category": "crop"},
    "soil_analysis":            {"name": "Soil Analysis",            "icon": "🌍", "category": "crop"},
    "fertilizer_optimization":  {"name": "Fertilizer Optimizer",     "icon": "🧪", "category": "crop"},
    "weather_risk":             {"name": "Weather Risk",             "icon": "⛅", "category": "crop"},
    "crop_planning":            {"name": "Crop Planning",            "icon": "📅", "category": "crop"},
    "market_intelligence":      {"name": "Market Intelligence",      "icon": "📈", "category": "market"},
    "livestock_health":         {"name": "Livestock Health",         "icon": "🐄", "category": "livestock"},
    "knowledge_base":           {"name": "Knowledge Base",           "icon": "📚", "category": "knowledge"},
}


@router.get("", summary="List all available agents")
async def list_agents(current_user: dict = Depends(get_current_user)):
    agents = []
    for agent_id in ALL_AGENTS:
        meta = AGENT_META.get(agent_id, {})
        agents.append({
            "id": agent_id,
            "name": meta.get("name", agent_id),
            "icon": meta.get("icon", "🤖"),
            "category": meta.get("category", "general"),
            "status": "active",
        })
    return {"agents": agents, "total": len(agents)}


class ImageAnalysisRequest(BaseModel):
    images: List[str]                  # base64-encoded image strings
    crop_type: Optional[str] = None
    additional_context: Optional[str] = None


@router.post("/analyze-image", summary="Run disease detection on uploaded images")
async def analyze_image(
    payload: ImageAnalysisRequest,
    current_user: dict = Depends(get_current_user),
):
    """Accepts 1–4 base64 images and returns a disease analysis report."""
    if not payload.images:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one image is required.")
    if len(payload.images) > 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum 4 images per request.")

    try:
        result = await analyze_images(
            images=payload.images,
            crop_type=payload.crop_type,
            context=payload.additional_context,
        )
        return result
    except Exception as exc:
        logger.error("image_analysis_error", extra={"error": str(exc)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image analysis failed. Please try again.",
        )


@router.get("/{agent_id}/status", summary="Check a specific agent's status")
async def agent_status(agent_id: str, current_user: dict = Depends(get_current_user)):
    if agent_id not in ALL_AGENTS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found.")
    return {"agent_id": agent_id, "status": "active", "model": "gpt-4o-mini"}