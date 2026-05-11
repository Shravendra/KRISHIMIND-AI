"""
Chat endpoint — routes requests to the multi-agent orchestrator.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Any, Optional, List, Dict
import time

from shared.auth.jwt import (
    get_current_user,
    UserInToken,
)

from shared.schemas.chat import (
    ChatRequest,
    ImageInput,
)

from shared.utils.logging import get_logger

from apps.chatbot_orchestrator.main import ChatbotOrchestrator


logger = get_logger("api.chat")

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


# Shared orchestrator
_orchestrator = ChatbotOrchestrator()


# ──────────────────────────────────────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────────────────────────────────────

class MessageHistoryItem(BaseModel):
    role: str
    content: str


class ChatPayload(BaseModel):
    message: str

    conversation_id: Optional[str] = None

    crop: Optional[str] = None

    season: Optional[str] = None

    history: Optional[List[MessageHistoryItem]] = []

    farm_context: Optional[Dict[str, Any]] = None

    images: Optional[List[str]] = []


# ──────────────────────────────────────────────────────────────────────────────
# Chat Endpoint
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "",
    summary="Send a message to KrishiMind-AI"
)
async def chat(
    payload: ChatPayload,
    current_user: UserInToken = Depends(get_current_user),
):
    """
    Main conversational endpoint.
    """

    start = time.perf_counter()

    try:

        # Convert image strings into ImageInput objects
        image_inputs = [
            ImageInput(
                url=f"upload_{i}",
                base64_data=img,
            )
            for i, img in enumerate(payload.images or [])
        ]

        request = ChatRequest(
            message=payload.message,

            farmer_id=current_user.farmer_id,

            crop=payload.crop
            or (payload.farm_context or {}).get("cropType"),

            season=payload.season,

            images=image_inputs,

            conversation_id=payload.conversation_id,

            conversation_history=[
                m.model_dump()
                for m in (payload.history or [])
            ],
        )

        response = await _orchestrator.handle_message(
            request
        )

    except Exception as exc:

        logger.exception(
            "chat_orchestrator_error",
            extra={
                "error": str(exc),
                "farmer_id": current_user.farmer_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="I encountered an error processing your request.",
        )

    elapsed_ms = (
        time.perf_counter() - start
    ) * 1000

    return {
        **response.model_dump(),
        "processing_time_ms": round(
            elapsed_ms,
            2,
        ),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Chat History
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/history/{session_id}",
    summary="Retrieve chat history"
)
async def get_history(
    session_id: str,
    limit: int = 20,
    current_user: UserInToken = Depends(
        get_current_user
    ),
):

    return {
        "session_id": session_id,
        "messages": [],
        "limit": limit,
        "note": (
            "Persistent history requires Redis."
        ),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Clear History
# ──────────────────────────────────────────────────────────────────────────────

@router.delete(
    "/history/{session_id}",
    summary="Clear chat history"
)
async def clear_history(
    session_id: str,
    current_user: UserInToken = Depends(
        get_current_user
    ),
):

    return {
        "cleared": True,
        "session_id": session_id,
    }