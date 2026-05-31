from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class MessageResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    conversation_id: str

    role: str

    content: str

    created_at: datetime