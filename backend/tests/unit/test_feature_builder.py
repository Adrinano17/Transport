"""Unit tests — FeatureBuilder and TrafficService (Lagos)."""

from datetime import datetime, timezone

import pytest

from lagos_fare.application.services.feature_builder import FeatureBuilder
from lagos_fare.application.services.traffic_service import TrafficService
from lagos_fare.domain.entities.geo_location import GeoLocation
from lagos_fare.domain.entities.trip_request import TripRequest
from lagos_fare.domain.ports.route_provider import RouteInfo
from lagos_fare.domain.ports.weather_provider import WeatherInfo
from lagos_fare.domain.value_objects.traffic_level import TrafficLevel
from lagos_fare.domain.value_objects.transport_type import TransportType
from lagos_fare.domain.value_objects.weather_condition import WeatherCondition
from tests.helpers import FEATURE_NAMES


@pytest.fixture
def sample_trip() -> TripRequest:
    return TripRequest(
        pickup=GeoLocation(6.5774, 3.3212, "Airport"),
        dropoff=GeoLocation(6.4281, 3.4219, "Victoria Island"),
        requested_at=datetime(2025, 6, 3, 7, 30, tzinfo=timezone.utc),  # 8:30 WAT rush
        passenger_count=2,
        transport_type=TransportType.BOLT,
    )


class TestFeatureBuilder:
    def test_builds_lagos_features(self, sample_trip) -> None:
        builder = FeatureBuilder(timezone="Africa/Lagos", feature_names=FEATURE_NAMES)
        route = RouteInfo(20.0, 40.0)
        weather = WeatherInfo("rain", 27.0, 80.0, 2.0)
        features = builder.build(
            sample_trip, route, weather, TrafficLevel.HEAVY, WeatherCondition.RAINY,
        )
        assert features.values["distance_km"] == 20.0
        assert "traffic_level" in features.values

    def test_rush_hour_flag(self, sample_trip) -> None:
        builder = FeatureBuilder(timezone="Africa/Lagos", feature_names=("is_rush_hour",))
        features = builder.build(
            sample_trip,
            RouteInfo(10.0, 20.0),
            WeatherInfo("sunny", 30.0, 70.0, 0.0),
            TrafficLevel.MODERATE,
            WeatherCondition.SUNNY,
        )
        assert features.values["is_rush_hour"] == 1.0


class TestTrafficService:
    def test_heavy_traffic_rush_hour_lagos(self) -> None:
        svc = TrafficService("Africa/Lagos")
        at = datetime(2025, 6, 3, 7, 30, tzinfo=timezone.utc)
        level = svc.get_level(at, RouteInfo(15.0, 45.0))
        assert level in (TrafficLevel.HEAVY, TrafficLevel.GRIDLOCK, TrafficLevel.MODERATE)
