from __future__ import annotations

from typing import List, Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
)


# ------------------------------------------------------------------
# Register
# ------------------------------------------------------------------

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

    phone: Optional[str] = None
    location: Optional[str] = None

    primary_crops: List[str] = Field(
        default_factory=list
    )

    land_size_acres: Optional[float] = None


# ------------------------------------------------------------------
# Login
# ------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ------------------------------------------------------------------
# Token Response
# ------------------------------------------------------------------

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    farmer_id: str
    name: str
    role: str


# ------------------------------------------------------------------
# Profile
# ------------------------------------------------------------------

class UserProfileResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    farmer_id: str
    name: str
    email: str

    role: str

    phone: Optional[str]
    location: Optional[str]

    primary_crops: Optional[list[str]]

    land_size_acres: Optional[float]

    is_active: bool


# ------------------------------------------------------------------
# Profile Update
# ------------------------------------------------------------------

class ProfileUpdateRequest(BaseModel):

    phone: Optional[str] = None

    location: Optional[str] = None

    primary_crops: Optional[List[str]] = None

    land_size_acres: Optional[float] = None