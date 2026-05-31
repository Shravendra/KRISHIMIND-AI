from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.db.models.user import User


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user: User,
    ) -> User:

        self.db.add(user)

        await self.db.commit()

        await self.db.refresh(user)

        return user

    async def get_by_id(
        self,
        farmer_id: str,
    ) -> Optional[User]:

        stmt = select(User).where(
            User.farmer_id == farmer_id
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> Optional[User]:

        stmt = select(User).where(
            User.email == email
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def update_profile(
        self,
        farmer_id: str,
        updates: dict,
    ) -> Optional[User]:

        user = await self.get_by_id(
            farmer_id
        )

        if not user:
            return None

        for key, value in updates.items():

            if hasattr(user, key):
                setattr(
                    user,
                    key,
                    value,
                )

        await self.db.commit()

        await self.db.refresh(user)

        return user

    async def deactivate_user(
        self,
        farmer_id: str,
    ) -> bool:

        user = await self.get_by_id(
            farmer_id
        )

        if not user:
            return False

        user.is_active = False

        await self.db.commit()

        return True

    async def delete(
        self,
        farmer_id: str,
    ) -> bool:

        user = await self.get_by_id(
            farmer_id
        )

        if not user:
            return False

        await self.db.delete(user)

        await self.db.commit()

        return True