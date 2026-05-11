"""
apps/api_gateway/routes/auth.py
────────────────────────────────
Authentication routes: register, login, me, logout.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

from shared.auth.jwt import create_access_token, get_current_user, UserInToken, verify_password
from shared.auth.user_store import user_store

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Request / Response Schemas ────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: Optional[str] = None
    location: Optional[str] = None
    primary_crops: List[str] = Field(default_factory=list)
    land_size_acres: Optional[float] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    farmer_id: str
    name: str
    role: str


class UserProfileResponse(BaseModel):
    farmer_id: str
    name: str
    email: str
    role: str
    phone: Optional[str]
    location: Optional[str]
    primary_crops: List[str]
    land_size_acres: Optional[float]
    is_active: bool


class ProfileUpdateRequest(BaseModel):
    phone: Optional[str] = None
    location: Optional[str] = None
    primary_crops: Optional[List[str]] = None
    land_size_acres: Optional[float] = None


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    """Register a new farmer account."""
    try:
        user = user_store.create(
            name=body.name,
            email=body.email,
            password=body.password,
            phone=body.phone,
            location=body.location,
            primary_crops=body.primary_crops,
            land_size_acres=body.land_size_acres,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    token = create_access_token({"sub": user.farmer_id, "name": user.name, "role": user.role})
    return TokenResponse(
        access_token=token,
        farmer_id=user.farmer_id,
        name=user.name,
        role=user.role,
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    """Login with email and password."""
    user = user_store.get_by_email(body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    token = create_access_token({"sub": user.farmer_id, "name": user.name, "role": user.role})
    return TokenResponse(
        access_token=token,
        farmer_id=user.farmer_id,
        name=user.name,
        role=user.role,
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_profile(current_user: UserInToken = Depends(get_current_user)):
    """Get current user profile."""
    user = user_store.get_by_id(current_user.farmer_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserProfileResponse(**user.model_dump())


@router.put("/me", response_model=UserProfileResponse)
async def update_profile(
    body: ProfileUpdateRequest,
    current_user: UserInToken = Depends(get_current_user),
):
    """Update farmer profile."""
    updates = body.model_dump(exclude_none=True)
    user = user_store.update_profile(current_user.farmer_id, updates)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserProfileResponse(**user.model_dump())


@router.post("/logout")
async def logout(current_user: UserInToken = Depends(get_current_user)):
    """
    Logout endpoint.
    Since we use stateless JWT, client must delete the token.
    Production: add token to Redis blacklist here.
    """
    return {"message": f"Successfully logged out, {current_user.name}"}


@router.get("/demo-credentials")
async def demo_credentials():
    """Return demo login credentials for testing."""
    return {
        "message": "Use these credentials to test the platform",
        "demo_farmer": {"email": "demo@krishimind.ai", "password": "demo1234"},
        "demo_admin": {"email": "admin@krishimind.ai", "password": "admin1234"},
    }
