"""
shared/auth/user_store.py
─────────────────────────
Simple in-memory user registry for local development.
Replace with async SQLAlchemy repository in production.
"""

from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel, EmailStr, Field

from shared.auth.jwt import hash_password


# ──────────────────────────────────────────────────────────────────────────────
# User Schema
# ──────────────────────────────────────────────────────────────────────────────

class UserRecord(BaseModel):
    farmer_id: str
    name: str
    email: EmailStr
    hashed_password: str
    role: str = "farmer"

    phone: Optional[str] = None
    location: Optional[str] = None

    primary_crops: list[str] = Field(default_factory=list)

    land_size_acres: Optional[float] = None

    is_active: bool = True


# ──────────────────────────────────────────────────────────────────────────────
# Seed Data
# ──────────────────────────────────────────────────────────────────────────────

_USERS: Dict[str, UserRecord] = {
    "demo@krishimind.ai": UserRecord(
        farmer_id="farmer-demo-001",
        name="Gopal Singh",
        email="demo@krishimind.ai",
        hashed_password=hash_password("demo1234"),
        role="farmer",
        phone="+91-9821661573",
        location="Bhabhua, Bihar",
        primary_crops=[
            "Paddy",
            "Mustered",
            "Wheat"
        ],
        land_size_acres=12.5,
    ),

    "admin@krishimind.ai": UserRecord(
        farmer_id="admin-001",
        name="Platform Admin",
        email="admin@krishimind.ai",
        hashed_password=hash_password("admin1234"),
        role="admin",
    ),
}


# ──────────────────────────────────────────────────────────────────────────────
# User Store
# ──────────────────────────────────────────────────────────────────────────────

class UserStore:

    def get_by_email(
        self,
        email: str
    ) -> Optional[UserRecord]:

        return _USERS.get(email.lower())


    def get_by_id(
        self,
        farmer_id: str
    ) -> Optional[UserRecord]:

        for user in _USERS.values():
            if user.farmer_id == farmer_id:
                return user

        return None


    def create(
        self,
        name: str,
        email: str,
        password: str,
        phone: Optional[str] = None,
        location: Optional[str] = None,
        primary_crops: Optional[list[str]] = None,
        land_size_acres: Optional[float] = None,
    ) -> UserRecord:

        email = email.lower()

        if email in _USERS:
            raise ValueError(
                f"Email already registered: {email}"
            )

        import uuid

        user = UserRecord(
            farmer_id=f"farmer-{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role="farmer",
            phone=phone,
            location=location,
            primary_crops=primary_crops or [],
            land_size_acres=land_size_acres,
        )

        _USERS[email] = user

        return user


    def update_profile(
        self,
        farmer_id: str,
        updates: dict
    ) -> Optional[UserRecord]:

        user = self.get_by_id(farmer_id)

        if not user:
            return None

        for key, value in updates.items():

            if key in {
                "hashed_password",
                "farmer_id",
            }:
                continue

            if hasattr(user, key):
                setattr(user, key, value)

        return user


user_store = UserStore()