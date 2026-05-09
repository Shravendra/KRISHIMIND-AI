from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ImageAnalysisRequest(BaseModel):
    image_inputs: List[Dict[str, Any]] = Field(default_factory=list)
    crop_type: Optional[str] = None
    location: Optional[Dict[str, Any]] = None

class ImageFinding(BaseModel):
    label: str
    severity: str
    confidence: float
    description: str

class ImageAnalysisResponse(BaseModel):
    findings: List[ImageFinding] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    summary: str = ""
