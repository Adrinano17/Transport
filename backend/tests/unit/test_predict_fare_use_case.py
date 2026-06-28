"""
Unit tests — PredictFareUseCase validation and orchestration.
"""

from datetime import datetime, timezone

import pytest

from lagos_fare.application.dto.trip_request_dto import GeoPointDTO, TripRequestDTO
from lagos_fare.domain.exceptions import InvalidCoordinatesError, SameLocationError


class TestPredictFareValidation:
    @pytest.mark.asyncio
    async def test_successful_prediction(self, predict_use_case, valid_prediction_payload) -> None:
        dto = TripRequestDTO(**valid_prediction_payload)
        result = await predict_use_case.execute(dto)

        assert result.predicted_fare_ngn > 0
        assert result.distance_km == pytest.approx(18.5)
        assert result.duration_min == pytest.approx(35.0)
        assert result.traffic_level in ("low", "moderate", "heavy", "gridlock")
        assert result.model_version == "lagos-fare-engine-v1"
        assert result.currency == "NGN"
        assert result.temperature_c == 28.0

    @pytest.mark.asyncio
    async def test_rejects_out_of_bounds_pickup(self, predict_use_case) -> None:
        dto = TripRequestDTO(
            pickup=GeoPointDTO(latitude=5.0, longitude=3.0),
            dropoff=GeoPointDTO(latitude=6.4281, longitude=3.4219),
        )
        with pytest.raises(InvalidCoordinatesError):
            await predict_use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_rejects_same_pickup_and_dropoff(self, predict_use_case) -> None:
        dto = TripRequestDTO(
            pickup=GeoPointDTO(latitude=6.5774, longitude=3.3212),
            dropoff=GeoPointDTO(latitude=6.5774, longitude=3.3212),
        )
        with pytest.raises(SameLocationError):
            await predict_use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_weather_failure_uses_neutral_defaults(
        self,
        test_settings,
        db_session,
        fare_model,
        mock_route,
    ) -> None:
        from lagos_fare.application.services.feature_builder import FeatureBuilder
        from lagos_fare.application.services.lagos_fare_engine import LagosFareEngine
        from lagos_fare.application.services.traffic_service import TrafficService
        from lagos_fare.application.use_cases.predict_fare import PredictFareUseCase
        from lagos_fare.infrastructure.db.sqlite_prediction_repository import SqlitePredictionRepository
        from tests.helpers import MockWeatherProvider

        failing_weather = MockWeatherProvider(should_fail=True)
        use_case = PredictFareUseCase(
            route_provider=mock_route,
            weather_provider=failing_weather,
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

        dto = TripRequestDTO(
            pickup=GeoPointDTO(latitude=6.5774, longitude=3.3212),
            dropoff=GeoPointDTO(latitude=6.4281, longitude=3.4219),
            requested_at=datetime(2025, 6, 3, 18, 0, tzinfo=timezone.utc),
        )
        result = await use_case.execute(dto)
        assert result.weather_condition == "sunny"
        assert result.temperature_c == 20.0
