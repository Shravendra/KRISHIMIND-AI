from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy import desc

from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession

from apps.db.models.conversation import Conversation
from apps.db.models.message import Message


class ConversationRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create_conversation(
        self,
        conversation: Conversation,
    ) -> Conversation:

        self.db.add(
            conversation
        )

        await self.db.commit()

        await self.db.refresh(
            conversation
        )

        return conversation

    async def get_conversation(
        self,
        conversation_id: str,
    ) -> Optional[Conversation]:

        stmt = (
            select(
                Conversation
            )
            .options(
                selectinload(
                    Conversation.messages
                )
            )
            .where(
                Conversation.id
                == conversation_id
            )
        )

        result = await self.db.execute(
            stmt
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_farmer_conversations(
        self,
        farmer_id: str,
        limit: int = 20,
    ) -> list[Conversation]:

        stmt = (
            select(
                Conversation
            )
            .where(
                Conversation.farmer_id
                == farmer_id
            )
            .order_by(
                desc(
                    Conversation.created_at
                )
            )
            .limit(limit)
        )

        result = await self.db.execute(
            stmt
        )

        return list(
            result.scalars().all()
        )

    async def add_message(
        self,
        message: Message,
    ) -> Message:

        self.db.add(message)

        await self.db.commit()

        await self.db.refresh(message)

        return message

    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 100,
    ) -> list[Message]:

        stmt = (
            select(
                Message
            )
            .where(
                Message.conversation_id
                == conversation_id
            )
            .order_by(
                Message.created_at
            )
            .limit(limit)
        )

        result = await self.db.execute(
            stmt
        )

        return list(
            result.scalars().all()
        )

    async def clear_conversation(
        self,
        conversation_id: str,
    ) -> bool:

        conversation = (
            await self.get_conversation(
                conversation_id
            )
        )

        if not conversation:
            return False

        await self.db.delete(
            conversation
        )

        await self.db.commit()

        return True
    
    async def verify_ownership(self,conversation_id: str, farmer_id: str,):
        stmt = select(Conversation).where(Conversation.id== conversation_id, 
                                          Conversation.farmer_id== farmer_id,
    )

        result = await self.db.execute(
            stmt
        )

        return result.scalar_one_or_none()