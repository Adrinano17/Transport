"""Generate analytics charts from SQLite prediction logs."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from lagos_fare.application.services.analytics_service import AnalyticsService
from lagos_fare.application.services.prediction_log_service import PredictionLogService
from lagos_fare.config import get_settings
from lagos_fare.infrastructure.db.database import get_session_factory, init_db
from lagos_fare.infrastructure.db.sqlite_prediction_repository import SqlitePredictionRepository


async def main() -> None:
    settings = get_settings()
    await init_db()
    factory = get_session_factory()
    async with factory() as session:
        log_service = PredictionLogService(SqlitePredictionRepository(session))
        records = await log_service.get_all_records()
        if not records:
            print("No predictions in database.")
            return
        analytics = AnalyticsService(settings.analytics_output_dir)
        paths = analytics.generate_all_charts(records)
        for p in paths:
            print(f"  Chart: {p}")


if __name__ == "__main__":
    asyncio.run(main())
