from datetime import datetime
from sqlalchemy import JSON
from sqlalchemy import (
    String,
    Boolean,
    Float,
    DateTime,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from apps.db.session import Base


class User(Base):

    __tablename__ = "users"

    farmer_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(30),
        default="farmer",
    )

    phone: Mapped[str | None] = mapped_column(
        String(20)
    )

    location: Mapped[str | None] = mapped_column(
        String(255)
    )

    primary_crops: Mapped[list | None] = mapped_column(
    JSON,
    nullable=True,
    )

    land_size_acres: Mapped[float | None] = mapped_column(
        Float
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    conversations = relationship(
    "Conversation",
    back_populates="user",
    cascade="all, delete-orphan",
    )