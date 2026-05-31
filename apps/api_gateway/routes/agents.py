"""
Agent management routes.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from shared.auth.jwt import (
    get_current_user,
    UserInToken,
)

from shared.constants.app import (
    ALL_AGENTS,
)

from shared.utils.logging import (
    get_logger,
)

from apps.db.schemas.image_analysis_schemas import (
    ImageAnalysisRequest,
)

from apps.db.services.image_analysis_service import (
    ImageAnalysisService,
)

from apps.db.dependencies import (
    get_image_analysis_service,
)

logger = get_logger("api.agents")

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
)


# ============================================================
# AGENT METADATA
# ============================================================

AGENT_META = {
    "disease_detection": {
        "name": "Disease Detection",
        "icon": "🔬",
        "category": "crop",
        "description": "Detect and identify crop diseases"
    },
    "soil_analysis": {
        "name": "Soil Analysis",
        "icon": "🌍",
        "category": "crop",
        "description": "Analyze soil properties and nutrient content"
    },
    "fertilizer_optimization": {
        "name": "Fertilizer Optimizer",
        "icon": "🧪",
        "category": "crop",
        "description": "Optimize fertilizer application based on soil and crop needs"
    },
    "weather_risk": {
        "name": "Weather Risk",
        "icon": "⛅",
        "category": "crop",
        "description": "Assess weather-related risks to crop production"
    },
    "crop_planning": {
        "name": "Crop Planning",
        "icon": "📅",
        "category": "crop",
        "description": "Plan crop rotation and planting schedules"
    },
    "market_intelligence": {
        "name": "Market Intelligence",
        "icon": "📈",
        "category": "market",
        "description": "Provide insights into market trends and pricing"
    },
    "harvest_recommendation": {
        "name": "Harvest Recommendation",
        "icon": "🌾",
        "category": "crop",
        "description": "Recommend optimal harvest timing and methods"
    },
    "postharvest_management": {
        "name": "Post-Harvest Management",
        "icon": "📦",
        "category": "crop",
        "description": "Manage post-harvest handling and storage of agricultural produce"
    },
    "livestock_health": {
        "name": "Livestock Health",
        "icon": "🐄",
        "category": "livestock",
        "description": "Monitor and improve livestock health and welfare"
    },
    "knowledge_base": {
        "name": "Knowledge Base",
        "icon": "📚",
        "category": "knowledge",
        "description": "Access a comprehensive database of agricultural knowledge and best practices"
    },
}


# ============================================================
# LIST AGENTS
# ============================================================

@router.get(
    "",
    summary="List all available agents",
)
async def list_agents(
    current_user: UserInToken = Depends(
        get_current_user
    ),
):

    agents = []

    for agent_id in ALL_AGENTS:

        meta = AGENT_META.get(
            agent_id,
            {},
        )

        agents.append(
            {
                "id": agent_id,
                "name": meta.get(
                    "name",
                    agent_id,
                ),
                "icon": meta.get(
                    "icon",
                    "🤖",
                ),
                "category": meta.get(
                    "category",
                    "general",
                ),
                "description": meta.get(
                    "description",
                    "No description available."
                ),
                "status": "active",
            }
        )

    return {
        "agents": agents,
        "total": len(
            agents
        ),
    }


# ============================================================
# ANALYZE IMAGE
# ============================================================

@router.post(
    "/analyze-image",
    summary="Analyze crop disease images",
)
async def analyze_image(
    payload: ImageAnalysisRequest,
    current_user: UserInToken = Depends(
        get_current_user
    ),
    image_service: ImageAnalysisService = Depends(
        get_image_analysis_service
    ),
):

    if not payload.images:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "At least one image "
                "is required."
            ),
        )

    if len(payload.images) > 4:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Maximum 4 images "
                "allowed."
            ),
        )

    try:

        result = await image_service.analyze(
            farmer_id=current_user.farmer_id,
            images=payload.images,
            crop_type=payload.crop_type,
            additional_context=(
                payload.additional_context
            ),
        )

        return {
            "success": True,
            "farmer_id": (
                current_user.farmer_id
            ),
            "analysis": result,
        }

    except Exception as exc:

        logger.exception(
            "image_analysis_error",
            extra={
                "error": str(exc),
                "farmer_id": (
                    current_user.farmer_id
                ),
            },
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Image analysis failed."
            ),
        )


# ============================================================
# ANALYSIS HISTORY
# ============================================================

@router.get(
    "/analysis-history",
    summary="Get image analysis history",
)
async def analysis_history(
    limit: int = 20,
    current_user: UserInToken = Depends(
        get_current_user
    ),
    image_service: ImageAnalysisService = Depends(
        get_image_analysis_service
    ),
):

    records = (
        await image_service.get_history(
            farmer_id=current_user.farmer_id,
            limit=limit,
        )
    )

    return {
        "total": len(records),
        "history": [
            {
                "id": r.id,
                "crop_type": r.crop_type,
                "result": r.result_json,
                "created_at": r.created_at,
            }
            for r in records
        ],
    }


# ============================================================
# ANALYSIS DETAILS
# ============================================================

@router.get(
    "/analysis-history/{analysis_id}",
    summary="Get analysis details",
)
async def get_analysis(
    analysis_id: int,
    current_user: UserInToken = Depends(
        get_current_user
    ),
    image_service: ImageAnalysisService = Depends(
        get_image_analysis_service
    ),
):

    record = (
        await image_service.repository.get_by_id(
            analysis_id
        )
    )

    if not record:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    if (
        record.farmer_id
        != current_user.farmer_id
    ):

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    return {
        "id": record.id,
        "farmer_id": record.farmer_id,
        "crop_type": record.crop_type,
        "result": record.result_json,
        "created_at": record.created_at,
    }


# ============================================================
# DELETE ANALYSIS
# ============================================================

@router.delete(
    "/analysis-history/{analysis_id}",
    summary="Delete analysis record",
)
async def delete_analysis(
    analysis_id: int,
    current_user: UserInToken = Depends(
        get_current_user
    ),
    image_service: ImageAnalysisService = Depends(
        get_image_analysis_service
    ),
):

    record = (
        await image_service.repository.get_by_id(
            analysis_id
        )
    )

    if not record:

        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    if (
        record.farmer_id
        != current_user.farmer_id
    ):

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    deleted = (
        await image_service.repository.delete(
            analysis_id
        )
    )

    return {
        "deleted": deleted,
        "analysis_id": analysis_id,
    }


# ============================================================
# AGENT STATUS
# ============================================================

@router.get(
    "/{agent_id}/status",
    summary="Agent status",
)
async def agent_status(
    agent_id: str,
    current_user: UserInToken = Depends(
        get_current_user
    ),
):

    if agent_id not in ALL_AGENTS:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Agent '{agent_id}' "
                f"not found."
            ),
        )

    return {
        "agent_id": agent_id,
        "status": "active",
        "model": "gpt-4o-mini",
    }