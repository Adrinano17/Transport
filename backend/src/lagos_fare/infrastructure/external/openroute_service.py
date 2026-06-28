"""OpenRouteService adapter — driving distance and duration."""

from __future__ import annotations

import logging

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from lagos_fare.application.exceptions import ExternalServiceError
from lagos_fare.domain.entities.geo_location import GeoLocation
from lagos_fare.domain.ports.route_provider import RouteInfo, RouteProvider

logger = logging.getLogger(__name__)

ORS_DIRECTIONS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"


class OpenRouteServiceClient(RouteProvider):
    def __init__(self, api_key: str, client: httpx.AsyncClient | None = None) -> None:
        self._api_key = api_key
        self._client = client
        self._owns_client = client is None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            from lagos_fare.infrastructure.external.http_client import create_http_client

            self._client = create_http_client()
        return self._client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def get_route(self, pickup: GeoLocation, dropoff: GeoLocation) -> RouteInfo:
        if not self._api_key:
            return self._haversine_fallback(pickup, dropoff)

        client = await self._get_client()
        body = {
            "coordinates": [
                [pickup.longitude, pickup.latitude],
                [dropoff.longitude, dropoff.latitude],
            ],
        }
        headers = {"Authorization": self._api_key, "Content-Type": "application/json"}

        try:
            response = await client.post(ORS_DIRECTIONS_URL, json=body, headers=headers)
            response.raise_for_status()
            data = response.json()
            summary = data["routes"][0]["summary"]
            distance_km = summary["distance"] / 1000.0
            duration_min = summary["duration"] / 60.0
            return RouteInfo(distance_km=distance_km, duration_min=duration_min)
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            logger.warning("ORS failed (%s), using haversine fallback", exc)
            return self._haversine_fallback(pickup, dropoff)

    @staticmethod
    def _haversine_fallback(pickup: GeoLocation, dropoff: GeoLocation) -> RouteInfo:
        """Straight-line estimate when ORS key missing or API down."""
        from math import asin, cos, radians, sin, sqrt

        lat1, lon1 = radians(pickup.latitude), radians(pickup.longitude)
        lat2, lon2 = radians(dropoff.latitude), radians(dropoff.longitude)
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        km = 6371.0 * 2 * asin(sqrt(a))
        road_km = km * 1.3
        duration_min = (road_km / 30.0) * 60.0
        return RouteInfo(distance_km=road_km, duration_min=max(duration_min, 1.0))

    async def close(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
