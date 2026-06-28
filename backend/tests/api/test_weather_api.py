"""
API tests — POST /weather endpoint.
"""

import pytest
from httpx import AsyncClient


class TestWeatherAPI:
    @pytest.mark.asyncio
    async def test_fetch_weather_success(self, test_client: AsyncClient) -> None:
        response = await test_client.post(
            "/api/v1/weather",
            json={"latitude": 40.758, "longitude": -73.9855},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["temperature"] == 28.0
        assert body["humidity"] == 75.0
        assert body["rainfall"] == 0.0
        assert body["weather_condition"] == "clear sky"

    @pytest.mark.asyncio
    async def test_fetch_weather_invalid_coords(self, test_client: AsyncClient) -> None:
        response = await test_client.post(
            "/api/v1/weather",
            json={"latitude": 200, "longitude": -73.9855},
        )
        assert response.status_code == 422
