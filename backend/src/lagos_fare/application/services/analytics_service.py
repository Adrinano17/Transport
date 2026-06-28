"""
Analytics visualisation module — publication-quality charts for Chapter 4.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", context="paper", font_scale=1.1)
plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 300, "font.family": "serif"})


class AnalyticsService:
    def __init__(self, output_dir: str | Path) -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all_charts(self, records: list[dict]) -> list[Path]:
        if not records:
            raise ValueError("No records for analytics.")

        df = pd.DataFrame(records)
        paths: list[Path] = []

        paths.append(self._fare_distribution(df))
        paths.append(self._distance_vs_fare(df))
        paths.append(self._traffic_impact(df))
        paths.append(self._weather_impact(df))
        paths.append(self._transport_comparison(df))
        paths.append(self._prediction_volume(df))

        return paths

    def _fare_distribution(self, df: pd.DataFrame) -> Path:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(df["predicted_fare_ngn"], bins=30, kde=True, color="#1a5276", ax=ax)
        ax.set_xlabel("Predicted Fare (₦)")
        ax.set_ylabel("Frequency")
        ax.set_title("Figure 4.1: Distribution of Predicted Fares in Lagos")
        path = self._output_dir / "01_fare_distribution.png"
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def _distance_vs_fare(self, df: pd.DataFrame) -> Path:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(
            data=df, x="distance_km", y="predicted_fare_ngn",
            hue="transport_type", alpha=0.6, ax=ax,
        )
        ax.set_xlabel("Distance (km)")
        ax.set_ylabel("Fare (₦)")
        ax.set_title("Figure 4.2: Distance vs Predicted Fare by Transport Type")
        path = self._output_dir / "02_distance_vs_fare.png"
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def _traffic_impact(self, df: pd.DataFrame) -> Path:
        order = ["low", "moderate", "heavy", "gridlock"]
        agg = df.groupby("traffic_level")["predicted_fare_ngn"].mean().reindex(order).dropna()
        fig, ax = plt.subplots(figsize=(8, 5))
        agg.plot(kind="bar", color="#c0392b", ax=ax)
        ax.set_xlabel("Traffic Level")
        ax.set_ylabel("Average Fare (₦)")
        ax.set_title("Figure 4.3: Impact of Traffic on Average Fare")
        ax.tick_params(axis="x", rotation=0)
        path = self._output_dir / "03_traffic_impact.png"
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def _weather_impact(self, df: pd.DataFrame) -> Path:
        agg = df.groupby("weather_condition")["predicted_fare_ngn"].mean().sort_values()
        fig, ax = plt.subplots(figsize=(8, 5))
        agg.plot(kind="barh", color="#2980b9", ax=ax)
        ax.set_xlabel("Average Fare (₦)")
        ax.set_title("Figure 4.4: Impact of Weather on Average Fare")
        path = self._output_dir / "04_weather_impact.png"
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def _transport_comparison(self, df: pd.DataFrame) -> Path:
        fig, ax = plt.subplots(figsize=(9, 5))
        sns.boxplot(data=df, x="transport_type", y="predicted_fare_ngn", palette="Set2", ax=ax)
        ax.set_xlabel("Transport Type")
        ax.set_ylabel("Fare (₦)")
        ax.set_title("Figure 4.5: Fare Comparison Across Transport Types")
        path = self._output_dir / "05_transport_comparison.png"
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def _prediction_volume(self, df: pd.DataFrame) -> Path:
        df = df.copy()
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["date"] = df["created_at"].dt.date
        vol = df.groupby("date").size()
        fig, ax = plt.subplots(figsize=(8, 5))
        vol.plot(kind="line", marker="o", color="#27ae60", ax=ax)
        ax.set_xlabel("Date")
        ax.set_ylabel("Prediction Count")
        ax.set_title("Figure 4.6: Daily Prediction Volume")
        path = self._output_dir / "06_prediction_volume.png"
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path
