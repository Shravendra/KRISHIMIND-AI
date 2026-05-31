from __future__ import annotations

import time

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

from shared.schemas.chat import (
    ChatRequest,
    ImageInput,
)

from shared.utils.logging import (
    get_logger,
)

from apps.db.schemas.chat import (
    ChatPayload,
)

from apps.db.services.chat_service import (
    ChatService,
)

from apps.db.dependencies import (
    get_chat_service,
)

from apps.chatbot_orchestrator.main import (
    ChatbotOrchestrator,
)

logger = get_logger("api.chat")

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

_orchestrator = ChatbotOrchestrator()


# ============================================================
# CHAT
# ============================================================

@router.post(
    "",
    summary="Send a message to KrishiMind-AI",
)
async def chat(
    payload: ChatPayload,
    current_user: UserInToken = Depends(
        get_current_user
    ),
    chat_service: ChatService = Depends(
        get_chat_service
    ),
):

    start = time.perf_counter()

    try:

        # ----------------------------------------------------
        # Conversation
        # ----------------------------------------------------

        conversation = (
            await chat_service.get_or_create_conversation(
                farmer_id=current_user.farmer_id,
                conversation_id=payload.conversation_id,
                title=payload.message[:50],
            )
        )

        # ----------------------------------------------------
        # Save User Message
        # ----------------------------------------------------

        await chat_service.save_user_message(
            conversation_id=conversation.id,
            content=payload.message,
        )

        # ----------------------------------------------------
        # Images
        # ----------------------------------------------------

        image_inputs = [
            ImageInput(
                url=f"upload_{i}",
                base64_data=img,
            )
            for i, img in enumerate(
                payload.images or []
            )
        ]

        farm_context = (
            payload.farm_context
            or {}
        )

        # ----------------------------------------------------
        # Orchestrator Request
        # ----------------------------------------------------

        request = ChatRequest(
            message=payload.message,
            farmer_id=current_user.farmer_id,
            crop=payload.crop
            or farm_context.get(
                "cropType"
            ),
            season=payload.season,
            growth_stage=farm_context.get(
                "growth_stage"
            ),
            images=image_inputs,
            conversation_id=conversation.id,
            conversation_history=[
                m.model_dump()
                for m in (
                    payload.history
                    or []
                )
            ],
            soil_test_data=farm_context.get(
                "soil_test_data"
            ),
            fertilizer_context=farm_context.get(
                "fertilizer_context"
            ),
        )

        response = (
            await _orchestrator.handle_message(
                request
            )
        )

        # ----------------------------------------------------
        # Save Assistant Message
        # ----------------------------------------------------

        assistant_message = (
            getattr(
                response,
                "response",
                None,
            )
            or getattr(
                response,
                "message",
                None,
            )
            or str(response)
        )

        await chat_service.save_assistant_message(
            conversation_id=conversation.id,
            content=assistant_message,
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
            detail=(
                "Failed to process "
                "chat request."
            ),
        )

    elapsed_ms = (
        time.perf_counter()
        - start
    ) * 1000

    return {
        **response.model_dump(),
        "conversation_id": conversation.id,
        "processing_time_ms": round(
            elapsed_ms,
            2,
        ),
    }


# ============================================================
# HISTORY
# ============================================================

@router.get(
    "/history/{conversation_id}",
    summary="Get Chat History",
)
async def get_history(
    conversation_id: str,
    current_user: UserInToken = Depends(
        get_current_user
    ),
    chat_service: ChatService = Depends(
        get_chat_service
    ),
):

    messages = (
        await chat_service.get_history(
            conversation_id
        )
    )

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": (
                    m.created_at
                ),
            }
            for m in messages
        ],
    }


# ============================================================
# CLEAR HISTORY
# ============================================================

@router.delete(
    "/history/{conversation_id}",
    summary="Delete Conversation",
)
async def clear_history(
    conversation_id: str,
    current_user: UserInToken = Depends(
        get_current_user
    ),
    chat_service: ChatService = Depends(
        get_chat_service
    ),
):

    deleted = (
        await chat_service.clear_history(
            conversation_id
        )
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail=(
                "Conversation "
                "not found"
            ),
        )

    return {
        "deleted": True,
        "conversation_id": conversation_id,
    }


# ============================================================
# LIST CONVERSATIONS
# ============================================================

@router.get(
    "/conversations",
    summary="List User Conversations",
)
async def list_conversations(
    current_user: UserInToken = Depends(
        get_current_user
    ),
    chat_service: ChatService = Depends(
        get_chat_service
    ),
):

    conversations = (
        await chat_service.repo.get_farmer_conversations(
            current_user.farmer_id
        )
    )

    return {
        "total": len(
            conversations
        ),
        "conversations": [
            {
                "id": c.id,
                "title": c.title,
                "created_at": (
                    c.created_at
                ),
            }
            for c in conversations
        ],
    }