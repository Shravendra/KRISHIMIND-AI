from fastapi import APIRouter

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("")
async def list_agents():
    return {
        "agents": [
            "image_analysis",
            "disease_detection",
            "soil_agent",
            "fertilizer_agent",
            "weather_agent",
            "crop_planning_agent",
            "market_agent",
            "rag_knowledge_agent",
        ]
    }
