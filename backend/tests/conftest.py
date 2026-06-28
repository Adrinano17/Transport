"""
Pytest fixtures: in-memory DB, mocked providers, test client, ML artifact.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pytest
import pytest_asyncio
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from lagos_fare.application.services.feature_builder import FeatureBuilder
from lagos_fare.application.services.lagos_fare_engine import LagosFareEngine
from lagos_fare.application.services.traffic_service import TrafficService
from lagos_fare.application.use_cases.predict_fare import PredictFareUseCase
from lagos_fare.config import Settings, get_settings
from lagos_fare.dependencies import (
    get_fare_model,
    get_predict_fare_use_case,
    get_route_client,
    get_weather_client,
    get_weather_service,
    init_fare_model,
)
from lagos_fare.infrastructure.db.database import get_db_session
from tests.helpers import FEATURE_NAMES, MockRouteProvider, MockWeatherProvider
from lagos_fare.infrastructure.db.models import Base
from lagos_fare.infrastructure.db.sqlite_prediction_repository import SqlitePredictionRepository
from lagos_fare.infrastructure.ml.sklearn_fare_model import SklearnFareModel
from lagos_fare.main import create_app
from lagos_fare.presentation.api.errors import register_exception_handlers
from lagos_fare.presentation.api.v1.router import api_v1_router

def reset_app_singletons() -> None:
    import lagos_fare.dependencies as deps

    deps._fare_model = None
    get_settings.cache_clear()
    get_route_client.cache_clear()
    get_weather_client.cache_clear()


@pytest.fixture(autouse=True)
def _isolate_singletons() -> Generator[None, None, None]:
    reset_app_singletons()
    yield
    reset_app_singletons()


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    return Settings(
        debug=True,
        database_url="sqlite+aiosqlite:///:memory:",
        model_path=str(tmp_path / "test_model.pkl"),
        ors_api_key="",
        owm_api_key="",
        cors_origins=["http://localhost:5173"],
        service_timezone="Africa/Lagos",
        lat_min=6.35,
        lat_max=6.65,
        lng_min=2.95,
        lng_max=3.65,
    )


@pytest.fixture
def model_artifact_path(tmp_path: Path) -> Path:
    rng = np.random.default_rng(42)
    n = 200
    X = rng.uniform(0, 30, (n, len(FEATURE_NAMES)))
    y = 2.5 + X[:, 0] * 2.5 + X[:, 1] * 0.5 + rng.normal(0, 0.5, n)

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LinearRegression()),
    ])
    pipeline.fit(X, y)

    path = tmp_path / "test_model.pkl"
    joblib.dump(
        {
            "model": pipeline,
            "model_name": "linear_regression",
            "model_version": "linear_regression-test",
            "feature_names": list(FEATURE_NAMES),
            "target": "fare_amount",
        },
        path,
    )
    return path


@pytest.fixture
def fare_model(model_artifact_path: Path) -> SklearnFareModel:
    return SklearnFareModel(model_artifact_path)


@pytest.fixture
def mock_route() -> MockRouteProvider:
    return MockRouteProvider()


@pytest.fixture
def mock_weather() -> MockWeatherProvider:
    return MockWeatherProvider()


@pytest_asyncio.fixture
async def db_engine(test_settings: Settings):
    engine = create_async_engine(test_settings.database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest_asyncio.fixture
async def predict_use_case(
    test_settings: Settings,
    db_session: AsyncSession,
    fare_model: SklearnFareModel,
    mock_route: MockRouteProvider,
    mock_weather: MockWeatherProvider,
) -> PredictFareUseCase:
    return PredictFareUseCase(
        route_provider=mock_route,
        weather_provider=mock_weather,
        fare_model=fare_model,
        repository=SqlitePredictionRepository(db_session),
        feature_builder=FeatureBuilder(
            timezone=test_settings.service_timezone,
            feature_names=fare_model.feature_names,
        ),
        traffic_service=TrafficService(timezone=test_settings.service_timezone),
        fare_engine=LagosFareEngine(),
        settings=test_settings,
    )


def _build_test_app(
    test_settings: Settings,
    model_artifact_path: Path,
    mock_route: MockRouteProvider,
    mock_weather: MockWeatherProvider,
    db_engine,
) -> FastAPI:
    """Minimal FastAPI app for tests — no file-based lifespan side effects."""
    test_settings.model_path = str(model_artifact_path)
    init_fare_model(test_settings)

    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)

    async def override_settings() -> Settings:
        return test_settings

    async def override_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def override_use_case(
        session: AsyncSession = Depends(override_db),
    ) -> PredictFareUseCase:
        model = get_fare_model(test_settings)
        return PredictFareUseCase(
            route_provider=mock_route,
            weather_provider=mock_weather,
            fare_model=model,
            repository=SqlitePredictionRepository(session),
            feature_builder=FeatureBuilder(
                timezone=test_settings.service_timezone,
                feature_names=model.feature_names,
            ),
            traffic_service=TrafficService(timezone=test_settings.service_timezone),
            fare_engine=LagosFareEngine(),
            settings=test_settings,
        )

    app = FastAPI(title="Test App", version="test")
    register_exception_handlers(app)
    app.include_router(api_v1_router, prefix="/api/v1")

    app.dependency_overrides[get_settings] = override_settings
    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_predict_fare_use_case] = override_use_case
    app.dependency_overrides[get_weather_client] = lambda: mock_weather

    async def override_weather_service() -> MockWeatherProvider:
        return mock_weather

    app.dependency_overrides[get_weather_service] = override_weather_service

    return app


@pytest_asyncio.fixture
async def test_client(
    test_settings: Settings,
    model_artifact_path: Path,
    mock_route: MockRouteProvider,
    mock_weather: MockWeatherProvider,
    db_engine,
) -> AsyncGenerator[AsyncClient, None]:
    app = _build_test_app(test_settings, model_artifact_path, mock_route, mock_weather, db_engine)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def valid_prediction_payload() -> dict[str, Any]:
    return {
        "pickup": {"latitude": 6.5774, "longitude": 3.3212, "label": "Murtala Muhammed Airport"},
        "dropoff": {"latitude": 6.4281, "longitude": 3.4219, "label": "Victoria Island"},
        "transport_type": "bolt",
        "passenger_count": 2,
        "requested_at": datetime(2024, 6, 3, 8, 30, tzinfo=timezone.utc).isoformat(),
    }
