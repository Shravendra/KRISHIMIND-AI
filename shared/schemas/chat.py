from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Location(BaseModel):
    lat: float
    lon: float

class ImageInput(BaseModel):
    url: str
    caption: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    farmer_id: str = Field(default="anonymous")
    crop: Optional[str] = None
    season: Optional[str] = None
    location: Optional[Location] = None
    images: List[ImageInput] = Field(default_factory=list)
    conversation_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)

class AgentResult(BaseModel):
    name: str
    success: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    intent: str
    confidence: float
    answer: str
    follow_up_question: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    agent_results: List[AgentResult] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
