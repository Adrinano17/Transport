"""
API tests — health endpoints.
"""

import pytest
from httpx import AsyncClient


class TestHealthAPI:
    @pytest.mark.asyncio
    async def test_liveness_returns_ok(self, test_client: AsyncClient) -> None:
        response = await test_client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_readiness_returns_model_info(self, test_client: AsyncClient) -> None:
        response = await test_client.get("/api/v1/health/ready")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] in ("ready", "degraded")
        assert body["model"] == "ok"
        assert body["model_version"] == "linear_regression-test"
        assert body["fallback_active"] is False
