from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel


# ------------------------------------------------------------------
# History Message
# ------------------------------------------------------------------

class MessageHistoryItem(BaseModel):
    role: str
    content: str


# ------------------------------------------------------------------
# Chat Request
# ------------------------------------------------------------------

class ChatPayload(BaseModel):

    message: str

    conversation_id: Optional[str] = None

    crop: Optional[str] = None

    season: Optional[str] = None

    history: List[
        MessageHistoryItem
    ] = []

    farm_context: Optional[
        Dict[str, Any]
    ] = None

    images: List[str] = []


# ------------------------------------------------------------------
# Chat Response
# ------------------------------------------------------------------

class ChatResponse(BaseModel):

    conversation_id: str

    response: str

    agent_used: Optional[str] = None

    metadata: Dict[str, Any] = {}

    processing_time_ms: float


# ------------------------------------------------------------------
# History Response
# ------------------------------------------------------------------

class ChatHistoryResponse(BaseModel):

    conversation_id: str

    messages: List[
        MessageHistoryItem
    ]