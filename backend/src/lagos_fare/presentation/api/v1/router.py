from fastapi import APIRouter

from lagos_fare.presentation.api.v1 import health, locations, predictions, reports, weather

api_v1_router = APIRouter()
api_v1_router.include_router(health.router, tags=["health"])
api_v1_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_v1_router.include_router(weather.router, prefix="/weather", tags=["weather"])
api_v1_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_v1_router.include_router(reports.router, prefix="/admin", tags=["admin"])
