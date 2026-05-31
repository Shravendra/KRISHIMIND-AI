from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class ConversationResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: str

    farmer_id: str

    title: str | None

    created_at: datetime