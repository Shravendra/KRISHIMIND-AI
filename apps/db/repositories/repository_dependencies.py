from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from apps.db.session import get_db

from apps.db.repositories.user_repository import UserRepository
from apps.db.repositories.conversation_repository import ConversationRepository
from apps.db.repositories.image_analysis_repository import ImageAnalysisRepository


async def get_user_repository(
    db: AsyncSession = Depends(get_db),
):
    return UserRepository(db)


async def get_conversation_repository(
    db: AsyncSession = Depends(get_db),
):
    return ConversationRepository(db)


async def get_image_analysis_repository(
    db: AsyncSession = Depends(get_db),
):
    return ImageAnalysisRepository(db)