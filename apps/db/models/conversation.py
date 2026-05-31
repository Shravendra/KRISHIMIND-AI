from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from apps.db.session import Base


class Conversation(Base):

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    farmer_id: Mapped[str] = mapped_column(
        ForeignKey("users.farmer_id"),
        index=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(255)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id"),
        index=True,
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete",
    )

    user = relationship(
        "User",
        back_populates="conversations",
    )