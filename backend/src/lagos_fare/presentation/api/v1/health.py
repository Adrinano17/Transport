from fastapi import APIRouter, Depends

from sqlalchemy import text

from lagos_fare.config import Settings, get_settings
from lagos_fare.dependencies import get_fare_model
from lagos_fare.infrastructure.db.database import get_engine
from lagos_fare.infrastructure.ml.sklearn_fare_model import SklearnFareModel

router = APIRouter()


@router.get("/health")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(
    settings: Settings = Depends(get_settings),
    model: SklearnFareModel = Depends(get_fare_model),
) -> dict:
    db_status = "ok"
    try:
        async with get_engine().connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    model_status = "ok" if model.is_loaded else "fallback"
    status = "ready" if db_status == "ok" else "degraded"

    return {
        "status": status,
        "database": db_status,
        "model": model_status,
        "model_version": model.version,
        "fallback_active": not model.is_loaded,
    }
