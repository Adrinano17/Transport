"""
Dependency injection — wires infrastructure adapters to use cases.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from lagos_fare.application.services.feature_builder import FeatureBuilder
from lagos_fare.application.services.lagos_fare_engine import LagosFareEngine
from lagos_fare.application.services.traffic_service import TrafficService
from lagos_fare.application.use_cases.predict_fare import PredictFareUseCase
from lagos_fare.config import Settings, get_settings
from lagos_fare.infrastructure.db.database import get_db_session
from lagos_fare.infrastructure.db.sqlite_prediction_repository import SqlitePredictionRepository
from lagos_fare.infrastructure.external.openroute_service import OpenRouteServiceClient
from lagos_fare.infrastructure.external.openweather_map import OpenWeatherMapClient
from lagos_fare.infrastructure.ml.sklearn_fare_model import SklearnFareModel

# Singleton model loaded at startup
_fare_model: SklearnFareModel | None = None


def get_fare_model(settings: Settings | None = None) -> SklearnFareModel:
    global _fare_model
    if _fare_model is None:
        s = settings or get_settings()
        _fare_model = SklearnFareModel(s.model_path)
    return _fare_model


def init_fare_model(settings: Settings) -> SklearnFareModel:
    global _fare_model
    _fare_model = SklearnFareModel(settings.model_path)
    return _fare_model


@lru_cache
def get_route_client() -> OpenRouteServiceClient:
    s = get_settings()
    return OpenRouteServiceClient(s.ors_api_key)


@lru_cache
def get_weather_client() -> OpenWeatherMapClient:
    s = get_settings()
    return OpenWeatherMapClient(s.owm_api_key)


async def get_predict_fare_use_case(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> PredictFareUseCase:
    model = get_fare_model(settings)
    feature_builder = FeatureBuilder(
        timezone=settings.service_timezone,
        feature_names=model.feature_names,
    )
    return PredictFareUseCase(
        route_provider=get_route_client(),
        weather_provider=get_weather_client(),
        fare_model=model,
        repository=SqlitePredictionRepository(session),
        feature_builder=feature_builder,
        traffic_service=TrafficService(timezone=settings.service_timezone),
        fare_engine=LagosFareEngine(),
        settings=settings,
    )


async def get_weather_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> OpenWeatherMapClient:
    return get_weather_client()
