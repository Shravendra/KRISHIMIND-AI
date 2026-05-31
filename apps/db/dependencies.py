from fastapi import Depends

from apps.db.repositories.repository_dependencies import (
    get_user_repository,
    get_conversation_repository,
    get_image_analysis_repository,
)

from apps.db.repositories.user_repository import UserRepository
from apps.db.repositories.conversation_repository import ConversationRepository
from apps.db.repositories.image_analysis_repository import ImageAnalysisRepository

from apps.db.services.auth_service import AuthService
from apps.db.services.chat_service import ChatService
from apps.db.services.image_analysis_service import ImageAnalysisService


async def get_auth_service(
    repo: UserRepository = Depends(
        get_user_repository
    ),
):
    return AuthService(repo)


async def get_chat_service(
    repo: ConversationRepository = Depends(
        get_conversation_repository
    ),
):
    return ChatService(repo)


async def get_image_analysis_service(
    repo: ImageAnalysisRepository = Depends(
        get_image_analysis_repository
    ),
):
    return ImageAnalysisService(repo)