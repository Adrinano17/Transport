"""WeatherProvider port — current weather at a location."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from lagos_fare.domain.entities.geo_location import GeoLocation


@dataclass(frozen=True)
class WeatherInfo:
    summary: str
    temperature_c: float
    humidity: float
    precipitation_mm: float


class WeatherProvider(ABC):
    @abstractmethod
    async def get_weather(self, location: GeoLocation) -> WeatherInfo:
        """Return current conditions; implementations may degrade gracefully."""
