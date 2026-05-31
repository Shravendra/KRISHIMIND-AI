from __future__ import annotations

from apps.db.models.image_analysis import (
    ImageAnalysis,
)

from apps.db.repositories.image_analysis_repository import (
    ImageAnalysisRepository,
)

from agents.crop.image_analysis.service import (
    analyze_images,
)


class ImageAnalysisService:

    def __init__(
        self,
        repository: ImageAnalysisRepository,
    ):
        self.repository = repository

    async def analyze(
        self,
        farmer_id: str,
        images: list[str],
        crop_type: str | None,
        additional_context: str | None,
    ):

        result = await analyze_images(
            images=images,
            crop_type=crop_type,
            context=additional_context,
        )

        db_record = ImageAnalysis(
            farmer_id=farmer_id,
            crop_type=crop_type,
            result_json=result,
        )

        await self.repository.create(
            db_record
        )

        return result

    async def get_history(
        self,
        farmer_id: str,
        limit: int = 20,
    ):

        return await self.repository.get_farmer_history(
            farmer_id,
            limit,
        )