"""
Train fare prediction models (Linear Regression + Random Forest).

Evaluates MAE, RMSE, R² on hold-out test set, selects best model, saves via joblib.

Usage:
  python train_model.py
  python train_model.py --data-dir ../../data/processed/nyc_tlc --output ../../artifacts/model.pkl
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "nyc_tlc"
DEFAULT_OUTPUT = PROJECT_ROOT / "backend" / "artifacts" / "model.pkl"


def load_train_test(data_dir: Path) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    data_dir = Path(data_dir)
    X_train = pd.read_parquet(data_dir / "X_train.parquet")
    y_train = pd.read_parquet(data_dir / "y_train.parquet").squeeze()
    X_test = pd.read_parquet(data_dir / "X_test.parquet")
    y_test = pd.read_parquet(data_dir / "y_test.parquet").squeeze()
    return X_train, y_train, X_test, y_test


def evaluate(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
    }


def train_and_compare(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    random_state: int = 42,
) -> tuple[Pipeline, str, dict]:
    """Train LR and RF; return best pipeline, name, and comparison metrics."""
    feature_names = list(X_train.columns)

    candidates: dict[str, Pipeline] = {
        "linear_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LinearRegression()),
        ]),
        "random_forest": Pipeline([
            ("model", RandomForestRegressor(
                n_estimators=100,
                max_depth=16,
                min_samples_leaf=5,
                random_state=random_state,
                n_jobs=-1,
            )),
        ]),
    }

    results: dict[str, dict] = {}
    best_name = ""
    best_pipeline: Pipeline | None = None
    best_rmse = float("inf")

    for name, pipeline in candidates.items():
        logger.info("Training %s ...", name)
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        metrics = evaluate(y_test.values, preds)
        results[name] = metrics
        logger.info("%s — MAE: %.4f | RMSE: %.4f | R²: %.4f", name, metrics["mae"], metrics["rmse"], metrics["r2"])
        if metrics["rmse"] < best_rmse:
            best_rmse = metrics["rmse"]
            best_name = name
            best_pipeline = pipeline

    assert best_pipeline is not None
    return best_pipeline, best_name, results


def save_artifact(
    pipeline: Pipeline,
    model_name: str,
    feature_names: list[str],
    metrics: dict,
    output_path: Path,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": pipeline,
        "model_name": model_name,
        "model_version": f"{model_name}-v1",
        "feature_names": feature_names,
        "target": "fare_amount",
        "metrics": metrics,
    }
    joblib.dump(artifact, output_path)
    logger.info("Saved best model (%s) to %s", model_name, output_path)

    metrics_path = output_path.parent / "model_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump({"best_model": model_name, "comparison": metrics}, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train fare prediction models")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    if not (args.data_dir / "X_train.parquet").exists():
        raise FileNotFoundError(
            f"Training data not found in {args.data_dir}. Run nyc_tlc/prepare_data.py first."
        )

    X_train, y_train, X_test, y_test = load_train_test(args.data_dir)
    best_pipeline, best_name, comparison = train_and_compare(
        X_train, y_train, X_test, y_test, args.random_state
    )
    save_artifact(best_pipeline, best_name, list(X_train.columns), comparison, args.output)

    print("\n=== Model Comparison ===")
    for name, m in comparison.items():
        marker = " <-- BEST" if name == best_name else ""
        print(f"{name}: MAE={m['mae']:.4f} RMSE={m['rmse']:.4f} R²={m['r2']:.4f}{marker}")


if __name__ == "__main__":
    main()
