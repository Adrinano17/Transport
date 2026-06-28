"""Lagos weather categories for fare adjustment."""

from enum import Enum


class WeatherCondition(str, Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    THUNDERSTORM = "thunderstorm"

    @property
    def multiplier(self) -> float:
        return {
            WeatherCondition.SUNNY: 1.0,
            WeatherCondition.CLOUDY: 1.02,
            WeatherCondition.RAINY: 1.12,
            WeatherCondition.THUNDERSTORM: 1.25,
        }[self]

    @classmethod
    def from_owm_summary(cls, summary: str, precipitation_mm: float = 0.0) -> "WeatherCondition":
        """Map OpenWeatherMap text + rainfall to Lagos weather category."""
        s = summary.lower()
        if "thunder" in s or "storm" in s:
            return cls.THUNDERSTORM
        if precipitation_mm > 0.5 or "rain" in s or "drizzle" in s:
            return cls.RAINY
        if "cloud" in s or "overcast" in s or "mist" in s or "haze" in s:
            return cls.CLOUDY
        return cls.SUNNY
