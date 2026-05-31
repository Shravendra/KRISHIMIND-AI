from __future__ import annotations

import uuid

from apps.db.models.conversation import Conversation
from apps.db.models.message import Message

from apps.db.repositories.conversation_repository import (
    ConversationRepository,
)

from apps.chatbot_orchestrator.main import (
    ChatbotOrchestrator,
)


class ChatService:

    def __init__(
        self,
        conversation_repository: ConversationRepository,
    ):
        self.repo = conversation_repository

        self.orchestrator = (
            ChatbotOrchestrator()
        )

    async def create_conversation_if_needed(
        self,
        farmer_id: str,
        conversation_id: str | None,
        title: str | None,
    ):

        if conversation_id:

            existing = (
                await self.repo.get_conversation(
                    conversation_id
                )
            )

            if existing:
                return existing

        conversation = Conversation(
            id=str(uuid.uuid4()),
            farmer_id=farmer_id,
            title=title,
        )

        return await self.repo.create_conversation(
            conversation
        )

    async def save_user_message(
        self,
        conversation_id: str,
        content: str,
    ):

        message = Message(
            conversation_id=conversation_id,
            role="user",
            content=content,
        )

        return await self.repo.add_message(
            message
        )

    async def save_assistant_message(
        self,
        conversation_id: str,
        content: str,
    ):

        message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=content,
        )

        return await self.repo.add_message(
            message
        )

    async def get_history(
        self,
        conversation_id: str,
    ):

        return await self.repo.get_messages(
            conversation_id
        )

    async def clear_history(
        self,
        conversation_id: str,
    ):

        return await self.repo.clear_conversation(
            conversation_id
        )
    
    async def get_or_create_conversation(
    self,
    farmer_id: str,
    conversation_id: str | None,
    title: str | None = None,
    ):

        if conversation_id:

            existing = await self.repo.get_conversation(
                conversation_id
            )

            if existing:
                return existing

        conversation = Conversation(
            id=str(uuid.uuid4()),
            farmer_id=farmer_id,
            title=title,
        )

        return await self.repo.create_conversation(
            conversation
        )