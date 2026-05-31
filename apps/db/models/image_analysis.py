from datetime import datetime
from sqlalchemy import JSON
from sqlalchemy import (
    JSON,
    Integer,
    String,
    Text,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from apps.db.session import Base


class ImageAnalysis(Base):

    __tablename__ = "image_analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    farmer_id: Mapped[str] = mapped_column(
        String(50),
        index=True,
    )

    crop_type: Mapped[str | None] = mapped_column(
        String(100)
    )

    result_json: Mapped[dict] = mapped_column(
    JSON
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )