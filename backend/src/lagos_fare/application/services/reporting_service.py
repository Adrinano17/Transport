"""
Reporting module — generates summary tables from prediction logs.

Exports to CSV and Excel for dissertation / analyst use.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class ReportingService:
    def __init__(self, output_dir: str | Path) -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def generate_reports(self, records: list[dict]) -> dict[str, Path]:
        if not records:
            raise ValueError("No prediction records available for reporting.")

        df = pd.DataFrame(records)
        outputs: dict[str, Path] = {}

        # 1. Prediction summary table
        summary = df[
            ["id", "pickup_label", "dropoff_label", "transport_type",
             "distance_km", "duration_min", "predicted_fare_ngn", "created_at"]
        ].copy()
        outputs["prediction_summary"] = self._export(summary, "prediction_summary")

        # 2. Average fare table
        avg_fare = df.groupby(["transport_type", "traffic_level"], as_index=False).agg(
            avg_fare_ngn=("predicted_fare_ngn", "mean"),
            trip_count=("id", "count"),
            avg_distance_km=("distance_km", "mean"),
        ).round(2)
        outputs["average_fare"] = self._export(avg_fare, "average_fare")

        # 3. Distance analysis
        df["distance_band"] = pd.cut(
            df["distance_km"],
            bins=[0, 5, 10, 20, 50, 100],
            labels=["0-5km", "5-10km", "10-20km", "20-50km", "50km+"],
        )
        distance_analysis = df.groupby("distance_band", as_index=False).agg(
            avg_fare_ngn=("predicted_fare_ngn", "mean"),
            avg_duration_min=("duration_min", "mean"),
            trip_count=("id", "count"),
        ).round(2)
        outputs["distance_analysis"] = self._export(distance_analysis, "distance_analysis")

        # 4. Traffic impact
        traffic_impact = df.groupby("traffic_level", as_index=False).agg(
            avg_fare_ngn=("predicted_fare_ngn", "mean"),
            avg_duration_min=("duration_min", "mean"),
            trip_count=("id", "count"),
        ).round(2)
        outputs["traffic_impact"] = self._export(traffic_impact, "traffic_impact")

        # 5. Weather impact
        weather_impact = df.groupby("weather_condition", as_index=False).agg(
            avg_fare_ngn=("predicted_fare_ngn", "mean"),
            trip_count=("id", "count"),
        ).round(2)
        outputs["weather_impact"] = self._export(weather_impact, "weather_impact")

        return outputs

    def _export(self, df: pd.DataFrame, name: str) -> Path:
        csv_path = self._output_dir / f"{name}.csv"
        xlsx_path = self._output_dir / f"{name}.xlsx"
        df.to_csv(csv_path, index=False)
        df.to_excel(xlsx_path, index=False, sheet_name=name[:31])
        return csv_path
