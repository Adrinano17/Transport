"""SQLite prediction repository — insert and query prediction logs."""

from __future__ import annotations

import json
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from lagos_fare.domain.entities.fare_prediction import FarePrediction
from lagos_fare.domain.entities.trip_request import TripRequest
from lagos_fare.domain.ports.prediction_repository import PredictionRepository
from lagos_fare.domain.ports.route_provider import RouteInfo
from lagos_fare.domain.ports.weather_provider import WeatherInfo
from lagos_fare.infrastructure.db.models import LocationORM, PredictionORM


class SqlitePredictionRepository(PredictionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_or_create_location(self, loc) -> LocationORM:
        stmt = select(LocationORM).where(
            LocationORM.latitude == loc.latitude,
            LocationORM.longitude == loc.longitude,
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        row = LocationORM(latitude=loc.latitude, longitude=loc.longitude, label=loc.label)
        self._session.add(row)
        await self._session.flush()
        return row

    async def save(
        self,
        prediction: FarePrediction,
        *,
        trip: TripRequest,
        weather: WeatherInfo,
        route: RouteInfo,
        weather_condition: str,
    ) -> None:
        pickup = await self._get_or_create_location(trip.pickup)
        dropoff = await self._get_or_create_location(trip.dropoff)

        self._session.add(
            PredictionORM(
                id=str(prediction.id),
                pickup_location_id=pickup.id,
                dropoff_location_id=dropoff.id,
                pickup_label=trip.pickup.label,
                dropoff_label=trip.dropoff.label,
                distance_km=route.distance_km,
                duration_min=route.duration_min,
                traffic_level=prediction.traffic_level.value,
                transport_type=prediction.transport_type,
                temperature_c=weather.temperature_c,
                humidity=weather.humidity,
                precipitation_mm=weather.precipitation_mm,
                weather_condition=weather_condition,
                predicted_fare=float(prediction.predicted_fare_ngn),
                currency="NGN",
                model_version=prediction.model_version,
                features_json=json.dumps(prediction.features.values),
                requested_at=trip.requested_at,
            )
        )

    def _row_to_dict(self, row: PredictionORM) -> dict:
        return {
            "id": row.id,
            "pickup_label": row.pickup_label,
            "dropoff_label": row.dropoff_label,
            "pickup_lat": row.pickup_location.latitude if row.pickup_location else None,
            "pickup_lng": row.pickup_location.longitude if row.pickup_location else None,
            "dropoff_lat": row.dropoff_location.latitude if row.dropoff_location else None,
            "dropoff_lng": row.dropoff_location.longitude if row.dropoff_location else None,
            "distance_km": row.distance_km,
            "duration_min": row.duration_min,
            "traffic_level": row.traffic_level,
            "transport_type": row.transport_type,
            "weather_condition": row.weather_condition,
            "temperature_c": row.temperature_c,
            "humidity": row.humidity,
            "precipitation_mm": row.precipitation_mm,
            "predicted_fare_ngn": row.predicted_fare,
            "currency": row.currency,
            "model_version": row.model_version,
            "requested_at": row.requested_at.isoformat() if row.requested_at else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }

    async def get_by_id(self, prediction_id: UUID) -> dict | None:
        stmt = (
            select(PredictionORM)
            .options(
                joinedload(PredictionORM.pickup_location),
                joinedload(PredictionORM.dropoff_location),
            )
            .where(PredictionORM.id == str(prediction_id))
        )
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return self._row_to_dict(row) if row else None

    async def list_recent(self, page: int, page_size: int) -> tuple[list[dict], int]:
        total = (await self._session.execute(select(func.count()).select_from(PredictionORM))).scalar_one()
        offset = (page - 1) * page_size
        stmt = (
            select(PredictionORM)
            .options(
                joinedload(PredictionORM.pickup_location),
                joinedload(PredictionORM.dropoff_location),
            )
            .order_by(PredictionORM.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        rows = (await self._session.execute(stmt)).scalars().unique().all()
        return [self._row_to_dict(r) for r in rows], total

    async def fetch_all_for_analytics(self) -> list[dict]:
        stmt = (
            select(PredictionORM)
            .options(
                joinedload(PredictionORM.pickup_location),
                joinedload(PredictionORM.dropoff_location),
            )
            .order_by(PredictionORM.created_at.desc())
        )
        rows = (await self._session.execute(stmt)).scalars().unique().all()
        return [self._row_to_dict(r) for r in rows]
