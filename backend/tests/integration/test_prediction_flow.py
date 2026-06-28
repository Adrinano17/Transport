"""
Integration tests — end-to-end prediction flow with persistence.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from lagos_fare.infrastructure.db.models import LocationORM, PredictionORM


class TestPredictionIntegration:
    @pytest.mark.asyncio
    async def test_full_flow_persists_to_database(
        self,
        test_client: AsyncClient,
        valid_prediction_payload: dict,
        db_engine,
    ) -> None:
        """API request → use case → SQLite: verify locations and prediction rows."""
        response = await test_client.post("/api/v1/predictions", json=valid_prediction_payload)
        assert response.status_code == 200
        prediction_id = response.json()["id"]

        factory = async_sessionmaker(db_engine, expire_on_commit=False)
        async with factory() as session:
            pred_stmt = select(PredictionORM).where(PredictionORM.id == prediction_id)
            prediction = (await session.execute(pred_stmt)).scalar_one()

            assert prediction.distance_km == pytest.approx(18.5)
            assert prediction.duration_min == pytest.approx(35.0)
            assert prediction.predicted_fare > 0
            assert prediction.weather_condition == "sunny"
            assert prediction.model_version == "lagos-fare-engine-v1"
            assert prediction.transport_type == "bolt"

            loc_count = (await session.execute(select(LocationORM))).scalars().all()
            assert len(loc_count) == 2

    @pytest.mark.asyncio
    async def test_repeated_predictions_create_separate_records(
        self,
        test_client: AsyncClient,
        valid_prediction_payload: dict,
        db_engine,
    ) -> None:
        for _ in range(2):
            response = await test_client.post("/api/v1/predictions", json=valid_prediction_payload)
            assert response.status_code == 200

        factory = async_sessionmaker(db_engine, expire_on_commit=False)
        async with factory() as session:
            preds = (await session.execute(select(PredictionORM))).scalars().all()
            assert len(preds) == 2
            assert preds[0].id != preds[1].id

    @pytest.mark.asyncio
    async def test_route_provider_called_once_per_request(
        self,
        test_client: AsyncClient,
        valid_prediction_payload: dict,
        mock_route,
    ) -> None:
        mock_route.call_count = 0
        await test_client.post("/api/v1/predictions", json=valid_prediction_payload)
        assert mock_route.call_count == 1
