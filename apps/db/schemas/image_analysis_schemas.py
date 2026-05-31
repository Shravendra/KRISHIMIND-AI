from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict


# ------------------------------------------------------------------
# Analyze Image Request
# ------------------------------------------------------------------

class ImageAnalysisRequest(BaseModel):

    images: List[str]

    crop_type: Optional[str] = None

    additional_context: Optional[str] = None


# ------------------------------------------------------------------
# Analyze Image Response
# ------------------------------------------------------------------

class ImageAnalysisResponse(BaseModel):

    result: Dict[str, Any]

    crop_type: Optional[str]

    created_at: datetime


# ------------------------------------------------------------------
# DB Response
# ------------------------------------------------------------------

class ImageAnalysisDBResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    farmer_id: str

    crop_type: Optional[str]

    result_json: Dict[str, Any]

    created_at: datetime