from __future__ import annotations

import uuid

from passlib.context import CryptContext

from apps.db.models.user import User
from apps.db.repositories.user_repository import UserRepository
from shared.auth.jwt import (
    hash_password,
    verify_password,
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class AuthService:

    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self.user_repository = user_repository

    async def register(
        self,
        name: str,
        email: str,
        password: str,
        phone: str | None = None,
        location: str | None = None,
        primary_crops: list[str] | None = None,
        land_size_acres: float | None = None,
    ) -> User:

        existing = await self.user_repository.get_by_email(
            email
        )

        if existing:
            raise ValueError(
                "Email already exists"
            )

        user = User(
            farmer_id=str(uuid.uuid4()),
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role="farmer",
            phone=phone,
            location=location,
            primary_crops=primary_crops or [],
            land_size_acres=land_size_acres,
        )

        return await self.user_repository.create(
            user
        )

    async def login(
        self,
        email: str,
        password: str,
    ) -> User:

        user = await self.user_repository.get_by_email(
            email
        )

        if not user:
            raise ValueError(
                "Invalid email or password"
            )

        if not verify_password(password, user.hashed_password):
            raise ValueError(
                "Invalid email or password"
            )

        if not user.is_active:
            raise ValueError(
                "Account disabled"
            )

        return user

    async def get_profile(
        self,
        farmer_id: str,
    ) -> User | None:

        return await self.user_repository.get_by_id(
            farmer_id
        )

    async def update_profile(
        self,
        farmer_id: str,
        updates: dict,
    ):

        return await self.user_repository.update_profile(
            farmer_id,
            updates,
        )