from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy import desc

from sqlalchemy.ext.asyncio import AsyncSession

from apps.db.models.image_analysis import (
    ImageAnalysis,
)


class ImageAnalysisRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        analysis: ImageAnalysis,
    ) -> ImageAnalysis:

        self.db.add(
            analysis
        )

        await self.db.commit()

        await self.db.refresh(
            analysis
        )

        return analysis

    async def get_by_id(
        self,
        analysis_id: int,
    ) -> Optional[ImageAnalysis]:

        stmt = select(
            ImageAnalysis
        ).where(
            ImageAnalysis.id
            == analysis_id
        )

        result = await self.db.execute(
            stmt
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_farmer_history(
        self,
        farmer_id: str,
        limit: int = 50,
    ) -> list[ImageAnalysis]:

        stmt = (
            select(
                ImageAnalysis
            )
            .where(
                ImageAnalysis.farmer_id
                == farmer_id
            )
            .order_by(
                desc(
                    ImageAnalysis.created_at
                )
            )
            .limit(limit)
        )

        result = await self.db.execute(
            stmt
        )

        return list(
            result.scalars().all()
        )

    async def delete(
        self,
        analysis_id: int,
    ) -> bool:

        analysis = (
            await self.get_by_id(
                analysis_id
            )
        )

        if not analysis:
            return False

        await self.db.delete(
            analysis
        )

        await self.db.commit()

        return True