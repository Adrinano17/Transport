"""
Model evaluation on Lagos synthetic dataset.

Usage:
  python run_evaluation.py --data ../../data/processed/lagos/lagos_transport.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from lagos_fare.application.services.evaluation_service import EvaluationService

FEATURES = [
    "distance_km", "duration_minutes", "pickup_hour", "is_weekend",
    "traffic_level", "weather_condition", "transport_type",
]
TARGET = "fare_ngn"

TRAFFIC_MAP = {"low": 0, "moderate": 1, "heavy": 2, "gridlock": 3}
WEATHER_MAP = {"sunny": 0, "cloudy": 1, "rainy": 2, "thunderstorm": 3}
TRANSPORT_MAP = {"taxi": 0, "bolt": 1, "uber": 2, "keke": 3, "brt": 4, "danfo": 5}


def prepare_xy(df: pd.DataFrame):
    X = df.copy()
    X["traffic_level"] = X["traffic_level"].map(TRAFFIC_MAP)
    X["weather_condition"] = X["weather_condition"].map(WEATHER_MAP)
    X["transport_type"] = X["transport_type"].map(TRANSPORT_MAP)
    X = X[FEATURES].astype(float)
    y = df[TARGET].values
    return X, y


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, default="data/reports/lagos/evaluation")
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    X, y = prepare_xy(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        "linear_regression": Pipeline([("scaler", StandardScaler()), ("model", LinearRegression())]),
        "random_forest": RandomForestRegressor(n_estimators=100, max_depth=16, random_state=42),
    }

    evaluator = EvaluationService(args.output)
    best = None
    best_rmse = float("inf")

    for name, pipeline in models.items():
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        metrics = evaluator.evaluate(y_test, preds, model_name=name)
        print(f"{name}: MAE=₦{metrics['mae']:,.0f} RMSE=₦{metrics['rmse']:,.0f} R²={metrics['r2']:.4f} MAPE={metrics['mape']:.1f}%")
        if metrics["rmse"] < best_rmse:
            best_rmse = metrics["rmse"]
            best = name

    print(f"\nBest model: {best}")


if __name__ == "__main__":
    main()
