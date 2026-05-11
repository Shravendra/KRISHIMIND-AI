"""
shared/schemas/chat.py
──────────────────────
Pydantic models for the chat API layer.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Location(BaseModel):
    lat: float
    lon: float
    address: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"


class ImageInput(BaseModel):
    url: str
    caption: Optional[str] = None
    base64_data: Optional[str] = None   # for direct upload
    mime_type: str = "image/jpeg"


class ChatRequest(BaseModel):
    message: str
    farmer_id: str = Field(default="anonymous")
    crop: Optional[str] = None
    season: Optional[str] = None
    growth_stage: Optional[str] = None
    location: Optional[Location] = None
    images: List[ImageInput] = Field(default_factory=list)
    conversation_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    language: str = "en"
    soil_test_data: Optional[Dict[str, Any]] = None
    fertilizer_context: Optional[Dict[str, Any]] = None 


class AgentResult(BaseModel):
    name: str
    success: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    latency_ms: Optional[float] = None
    # Extended fields used by specialist agents
    summary: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    confidence: Optional[float] = None


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
    language: str = "en"


class FarmProfileUpdate(BaseModel):
    location: Optional[Location] = None
    land_size_acres: Optional[float] = None
    primary_crops: Optional[List[str]] = None
    irrigation_type: Optional[str] = None
    soil_type: Optional[str] = None
    season: Optional[str] = None
