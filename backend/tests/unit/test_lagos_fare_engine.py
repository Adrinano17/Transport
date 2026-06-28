"""Unit tests — Lagos Fare Estimation Engine."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from lagos_fare.application.services.lagos_fare_engine import LagosFareEngine
from lagos_fare.domain.value_objects.traffic_level import TrafficLevel
from lagos_fare.domain.value_objects.transport_type import TransportType
from lagos_fare.domain.value_objects.weather_condition import WeatherCondition


class TestLagosFareEngine:
    def test_bolt_fare_realistic_range(self) -> None:
        engine = LagosFareEngine()
        at = datetime(2025, 6, 3, 14, 0, tzinfo=timezone.utc)
        result = engine.calculate(
            distance_km=15.0,
            duration_min=35.0,
            transport_type=TransportType.BOLT,
            traffic=TrafficLevel.MODERATE,
            weather=WeatherCondition.SUNNY,
            requested_at=at,
        )
        fare = float(result.predicted_fare_ngn)
        assert 2000 <= fare <= 15000

    def test_keke_cheaper_than_bolt(self) -> None:
        engine = LagosFareEngine()
        at = datetime(2025, 6, 3, 14, 0, tzinfo=timezone.utc)
        keke = engine.calculate(10.0, 25.0, TransportType.KEKE, TrafficLevel.LOW, WeatherCondition.SUNNY, at)
        bolt = engine.calculate(10.0, 25.0, TransportType.BOLT, TrafficLevel.LOW, WeatherCondition.SUNNY, at)
        assert keke.predicted_fare_ngn < bolt.predicted_fare_ngn

    def test_gridlock_increases_fare(self) -> None:
        engine = LagosFareEngine()
        at = datetime(2025, 6, 3, 7, 30, tzinfo=timezone.utc)
        low = engine.calculate(12.0, 30.0, TransportType.TAXI, TrafficLevel.LOW, WeatherCondition.SUNNY, at)
        grid = engine.calculate(12.0, 30.0, TransportType.TAXI, TrafficLevel.GRIDLOCK, WeatherCondition.SUNNY, at)
        assert grid.predicted_fare_ngn > low.predicted_fare_ngn

    def test_minimum_fare_enforced(self) -> None:
        engine = LagosFareEngine()
        at = datetime(2025, 6, 3, 14, 0, tzinfo=timezone.utc)
        result = engine.calculate(0.5, 2.0, TransportType.BRT, TrafficLevel.LOW, WeatherCondition.SUNNY, at)
        assert result.predicted_fare_ngn >= Decimal("200")
