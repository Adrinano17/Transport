"""Generate reporting tables from SQLite prediction logs."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from lagos_fare.application.services.prediction_log_service import PredictionLogService
from lagos_fare.application.services.reporting_service import ReportingService
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
            print("No predictions in database. Run some predictions first.")
            return
        reporting = ReportingService(settings.reports_output_dir)
        outputs = reporting.generate_reports(records)
        for name, path in outputs.items():
            print(f"  {name}: {path}")


if __name__ == "__main__":
    asyncio.run(main())
