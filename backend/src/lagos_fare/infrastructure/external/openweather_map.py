"""OpenWeatherMap adapter — current weather at coordinates."""

from __future__ import annotations

import logging

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from lagos_fare.application.exceptions import ExternalServiceError
from lagos_fare.domain.entities.geo_location import GeoLocation
from lagos_fare.domain.ports.weather_provider import WeatherInfo, WeatherProvider

logger = logging.getLogger(__name__)

OWM_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


class OpenWeatherMapClient(WeatherProvider):
    NEUTRAL = WeatherInfo(
        summary="unknown",
        temperature_c=20.0,
        humidity=60.0,
        precipitation_mm=0.0,
    )

    def __init__(self, api_key: str, client: httpx.AsyncClient | None = None) -> None:
        self._api_key = api_key
        self._client = client
        self._owns_client = client is None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            from lagos_fare.infrastructure.external.http_client import create_http_client

            self._client = create_http_client()
        return self._client

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
    async def get_weather(self, location: GeoLocation) -> WeatherInfo:
        if not self._api_key:
            logger.warning("OWM_API_KEY not set — returning neutral weather")
            return self.NEUTRAL

        client = await self._get_client()
        params = {
            "lat": location.latitude,
            "lon": location.longitude,
            "appid": self._api_key,
            "units": "metric",
        }

        try:
            response = await client.get(OWM_WEATHER_URL, params=params)
            response.raise_for_status()
            data = response.json()
            rain = data.get("rain", {})
            precipitation = float(rain.get("1h", rain.get("3h", 0.0)))
            main = data["main"]
            weather = data["weather"][0]["description"] if data.get("weather") else "unknown"
            return WeatherInfo(
                summary=weather,
                temperature_c=float(main["temp"]),
                humidity=float(main["humidity"]),
                precipitation_mm=precipitation,
            )
        except (httpx.HTTPError, KeyError) as exc:
            logger.warning("OpenWeatherMap failed: %s", exc)
            raise ExternalServiceError(f"Weather service unavailable: {exc}", service="openweathermap") from exc

    async def close(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
