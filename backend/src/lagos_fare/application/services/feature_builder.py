"""
Builds ML feature dict for Lagos fare prediction.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from lagos_fare.domain.entities.trip_request import TripRequest
from lagos_fare.domain.ports.route_provider import RouteInfo
from lagos_fare.domain.ports.weather_provider import WeatherInfo
from lagos_fare.domain.value_objects.feature_vector import FeatureVector
from lagos_fare.domain.value_objects.traffic_level import TrafficLevel
from lagos_fare.domain.value_objects.transport_type import TransportType
from lagos_fare.domain.value_objects.weather_condition import WeatherCondition

TRAFFIC_ENCODING = {
    TrafficLevel.LOW: 0.0,
    TrafficLevel.MODERATE: 1.0,
    TrafficLevel.HEAVY: 2.0,
    TrafficLevel.GRIDLOCK: 3.0,
}

TRANSPORT_ENCODING = {
    TransportType.TAXI: 0,
    TransportType.BOLT: 1,
    TransportType.UBER: 2,
    TransportType.KEKE: 3,
    TransportType.BRT: 4,
    TransportType.DANFO: 5,
}


class FeatureBuilder:
    def __init__(self, timezone: str = "Africa/Lagos", feature_names: tuple[str, ...] = ()) -> None:
        self._tz = ZoneInfo(timezone)
        self._feature_names = feature_names

    def build(
        self,
        trip: TripRequest,
        route: RouteInfo,
        weather: WeatherInfo,
        traffic: TrafficLevel,
        weather_cat: WeatherCondition,
    ) -> FeatureVector:
        local_time = trip.requested_at.astimezone(self._tz)
        duration_min = route.duration_min
        avg_speed_kmh = (
            route.distance_km / (duration_min / 60.0) if duration_min > 0 else 0.0
        )

        is_rush = int(
            local_time.weekday() < 5
            and (7 <= local_time.hour <= 9 or 16 <= local_time.hour <= 19)
        )

        values: dict[str, float] = {
            "distance_km": route.distance_km,
            "duration_min": duration_min,
            "avg_speed_kmh": avg_speed_kmh,
            "passenger_count": float(trip.passenger_count),
            "pickup_hour": float(local_time.hour),
            "pickup_day_of_week": float(local_time.weekday()),
            "pickup_month": float(local_time.month),
            "is_weekend": float(local_time.weekday() >= 5),
            "is_rush_hour": float(is_rush),
            "traffic_level": TRAFFIC_ENCODING[traffic],
            "weather_level": float(list(WeatherCondition).index(weather_cat)),
            "transport_type": float(TRANSPORT_ENCODING[trip.transport_type]),
            "temperature_c": weather.temperature_c,
            "humidity": weather.humidity,
            "precipitation_mm": weather.precipitation_mm,
            "trip_duration_per_km": (
                duration_min / route.distance_km if route.distance_km > 0 else duration_min
            ),
        }

        if self._feature_names:
            values = {k: values.get(k, 0.0) for k in self._feature_names}

        return FeatureVector(values=values, feature_names=self._feature_names)
