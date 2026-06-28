"""Prediction logging — query service for stored fare predictions."""

from uuid import UUID

from lagos_fare.domain.ports.prediction_repository import PredictionRepository


class PredictionLogService:
    def __init__(self, repository: PredictionRepository) -> None:
        self._repo = repository

    async def get_by_id(self, prediction_id: UUID) -> dict | None:
        return await self._repo.get_by_id(prediction_id)

    async def list_predictions(self, page: int = 1, page_size: int = 20) -> dict:
        page_size = min(page_size, 100)
        items, total = await self._repo.list_recent(page, page_size)
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_all_records(self) -> list[dict]:
        return await self._repo.fetch_all_for_analytics()
