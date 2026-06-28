"""Shared test doubles and constants."""

from lagos_fare.domain.entities.geo_location import GeoLocation
from lagos_fare.domain.ports.route_provider import RouteInfo, RouteProvider
from lagos_fare.domain.ports.weather_provider import WeatherInfo, WeatherProvider

FEATURE_NAMES = (
    "distance_km",
    "duration_min",
    "avg_speed_kmh",
    "passenger_count",
    "pickup_hour",
    "pickup_day_of_week",
    "pickup_month",
    "is_weekend",
    "is_rush_hour",
    "traffic_level",
    "weather_level",
    "transport_type",
    "temperature_c",
    "humidity",
    "precipitation_mm",
    "trip_duration_per_km",
)


class MockRouteProvider(RouteProvider):
    def __init__(self, distance_km: float = 18.5, duration_min: float = 35.0) -> None:
        self.distance_km = distance_km
        self.duration_min = duration_min
        self.call_count = 0

    async def get_route(self, pickup: GeoLocation, dropoff: GeoLocation) -> RouteInfo:
        self.call_count += 1
        return RouteInfo(distance_km=self.distance_km, duration_min=self.duration_min)


class MockWeatherProvider(WeatherProvider):
    def __init__(
        self,
        summary: str = "clear sky",
        temperature_c: float = 28.0,
        humidity: float = 75.0,
        precipitation_mm: float = 0.0,
        should_fail: bool = False,
    ) -> None:
        self.summary = summary
        self.temperature_c = temperature_c
        self.humidity = humidity
        self.precipitation_mm = precipitation_mm
        self.should_fail = should_fail

    async def get_weather(self, location: GeoLocation) -> WeatherInfo:
        if self.should_fail:
            raise ConnectionError("Weather API unavailable")
        return WeatherInfo(
            summary=self.summary,
            temperature_c=self.temperature_c,
            humidity=self.humidity,
            precipitation_mm=self.precipitation_mm,
        )
