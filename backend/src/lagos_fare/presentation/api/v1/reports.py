"""Reporting and analytics API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from lagos_fare.application.services.analytics_service import AnalyticsService
from lagos_fare.application.services.prediction_log_service import PredictionLogService
from lagos_fare.application.services.reporting_service import ReportingService
from lagos_fare.config import Settings, get_settings
from lagos_fare.infrastructure.db.database import get_db_session
from lagos_fare.infrastructure.db.sqlite_prediction_repository import SqlitePredictionRepository

router = APIRouter()


async def get_log_service(session: AsyncSession = Depends(get_db_session)) -> PredictionLogService:
    return PredictionLogService(SqlitePredictionRepository(session))


@router.get("/predictions")
async def list_predictions(
    page: int = 1,
    page_size: int = 20,
    log_service: PredictionLogService = Depends(get_log_service),
) -> dict:
    return await log_service.list_predictions(page, page_size)


@router.post("/reports/generate")
async def generate_reports(
    settings: Settings = Depends(get_settings),
    log_service: PredictionLogService = Depends(get_log_service),
) -> dict:
    records = await log_service.get_all_records()
    if not records:
        raise HTTPException(status_code=404, detail="No prediction records found.")
    reporting = ReportingService(settings.reports_output_dir)
    outputs = reporting.generate_reports(records)
    return {"status": "ok", "files": {k: str(v) for k, v in outputs.items()}}


@router.post("/analytics/generate")
async def generate_analytics(
    settings: Settings = Depends(get_settings),
    log_service: PredictionLogService = Depends(get_log_service),
) -> dict:
    records = await log_service.get_all_records()
    if not records:
        raise HTTPException(status_code=404, detail="No prediction records found.")
    analytics = AnalyticsService(settings.analytics_output_dir)
    paths = analytics.generate_all_charts(records)
    return {"status": "ok", "charts": [str(p) for p in paths]}
