"""
API tests — POST /predictions validation and responses.
"""

import pytest
from httpx import AsyncClient


class TestPredictionsAPI:
    @pytest.mark.asyncio
    async def test_predict_fare_success(
        self,
        test_client: AsyncClient,
        valid_prediction_payload: dict,
    ) -> None:
        response = await test_client.post("/api/v1/predictions", json=valid_prediction_payload)
        assert response.status_code == 200

        body = response.json()
        assert "id" in body
        assert float(body["predicted_fare_ngn"]) > 0
        assert body["distance_km"] == pytest.approx(18.5)
        assert body["duration_min"] == pytest.approx(35.0)
        assert body["model_version"] == "lagos-fare-engine-v1"
        assert body["currency"] == "NGN"
        assert body["weather_condition"] == "sunny"
        assert body["transport_type"] == "bolt"

    @pytest.mark.asyncio
    async def test_predict_fare_missing_pickup_returns_422(self, test_client: AsyncClient) -> None:
        response = await test_client.post(
            "/api/v1/predictions",
            json={"dropoff": {"latitude": 40.758, "longitude": -73.9855}},
        )
        assert response.status_code == 422
        body = response.json()
        assert body["type"] == "validation_error"
        assert "errors" in body

    @pytest.mark.asyncio
    async def test_predict_fare_invalid_latitude_returns_422(self, test_client: AsyncClient) -> None:
        response = await test_client.post(
            "/api/v1/predictions",
            json={
                "pickup": {"latitude": 999, "longitude": -73.7781},
                "dropoff": {"latitude": 40.758, "longitude": -73.9855},
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_predict_fare_out_of_service_area_returns_400(
        self,
        test_client: AsyncClient,
    ) -> None:
        response = await test_client.post(
            "/api/v1/predictions",
            json={
                "pickup": {"latitude": 5.0, "longitude": 3.0},
                "dropoff": {"latitude": 6.4281, "longitude": 3.4219},
            },
        )
        assert response.status_code == 400
        assert response.json()["type"] == "invalid_coordinates"

    @pytest.mark.asyncio
    async def test_predict_fare_same_location_returns_400(self, test_client: AsyncClient) -> None:
        response = await test_client.post(
            "/api/v1/predictions",
            json={
                "pickup": {"latitude": 6.5774, "longitude": 3.3212},
                "dropoff": {"latitude": 6.5774, "longitude": 3.3212},
            },
        )
        assert response.status_code == 400
        assert response.json()["type"] == "same_location"

    @pytest.mark.asyncio
    async def test_predict_fare_passenger_count_bounds(self, test_client: AsyncClient) -> None:
        response = await test_client.post(
            "/api/v1/predictions",
            json={
                "pickup": {"latitude": 40.6413, "longitude": -73.7781},
                "dropoff": {"latitude": 40.758, "longitude": -73.9855},
                "passenger_count": 99,
            },
        )
        assert response.status_code == 422
