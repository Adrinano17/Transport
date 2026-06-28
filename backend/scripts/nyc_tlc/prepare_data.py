"""
NYC TLC Yellow Taxi — data preparation pipeline.

Steps:
  1. Load Parquet or CSV
  2. Drop invalid / corrupt rows
  3. Impute or drop missing values
  4. Remove statistical outliers
  5. Engineer fare-prediction features
  6. Time-based (or random) train/test split
  7. Persist cleaned data and feature matrices

Usage:
  python prepare_data.py --input ../../data/raw/nyc_tlc/yellow_tripdata_2024-01.parquet
  python prepare_data.py --input data.parquet --split random --no-outlier-removal
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Allow running as script from repo root or scripts/nyc_tlc/
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import DEFAULT_CONFIG, TLCConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. Load
# ---------------------------------------------------------------------------


def load_dataset(path: Path) -> pd.DataFrame:
    """Load NYC TLC file (Parquet preferred for speed and types)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    logger.info("Loading %s", path)
    if path.suffix.lower() == ".parquet":
        df = pd.read_parquet(path)
    elif path.suffix.lower() in {".csv", ".txt"}:
        df = pd.read_csv(path, low_memory=False)
    else:
        raise ValueError(f"Unsupported format: {path.suffix}. Use .parquet or .csv")

    logger.info("Loaded shape: %s", df.shape)
    return df


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and lower-case for robust matching."""
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    return df


# ---------------------------------------------------------------------------
# 2. Invalid rows
# ---------------------------------------------------------------------------


def remove_invalid_rows(df: pd.DataFrame, cfg: TLCConfig) -> pd.DataFrame:
    """
    Remove rows that violate NYC TLC business rules or are logically impossible.

    - Non-positive fare or distance (when distance > 0 expected for paid trips)
    - Dropoff before pickup
    - Coordinates/location IDs of 0 (when present)
    - Zero-distance trips with high fare (data entry errors)
    """
    n_start = len(df)
    df = df.copy()

    # Parse datetimes early
    for col in ("tpep_pickup_datetime", "tpep_dropoff_datetime"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Required numeric columns must exist
    missing_required = [c for c in cfg.required_columns if c not in df.columns]
    if missing_required:
        raise ValueError(f"Missing required columns: {missing_required}")

    # Drop rows with null pickup/dropoff times
    df = df.dropna(subset=["tpep_pickup_datetime", "tpep_dropoff_datetime"])

    # Dropoff must be after pickup
    duration = df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    valid_duration = (duration >= pd.Timedelta(0)) & (
        duration <= pd.Timedelta(hours=cfg.max_trip_duration_hours)
    )
    df = df.loc[valid_duration]

    # Fare and distance bounds
    df = df[df["fare_amount"].between(cfg.min_fare, cfg.max_fare)]
    df = df[df["trip_distance"].between(cfg.min_distance, cfg.max_distance)]

    # Invalid location IDs (NYC TLC uses 1–263 for zones; 264+ special)
    for loc_col in ("PULocationID", "DOLocationID"):
        if loc_col in df.columns:
            df = df[df[loc_col] > 0]

    # Passenger count
    if "passenger_count" in df.columns:
        df = df[df["passenger_count"].between(cfg.min_passengers, cfg.max_passengers)]

    # Remove zero-distance trips with fare above minimum (likely bad records)
    df = df[~((df["trip_distance"] == 0) & (df["fare_amount"] > cfg.min_fare + 1))]

    # Payment type: NYC TLC codes 1–6; 0 or null often means unknown
    if "payment_type" in df.columns:
        df = df[df["payment_type"].isin([1, 2, 3, 4, 5, 6])]

    logger.info("Invalid rows removed: %d -> %d (dropped %d)", n_start, len(df), n_start - len(df))
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3. Missing values
# ---------------------------------------------------------------------------


def handle_missing_values(df: pd.DataFrame, cfg: TLCConfig) -> pd.DataFrame:
    """
    Strategy:
    - Drop rows missing target or core features (distance, datetimes, locations)
    - Impute passenger_count with median (small missing rate in TLC data)
    - Impute optional fee columns with 0
    """
    n_start = len(df)
    df = df.copy()

    core = ["fare_amount", "trip_distance", "PULocationID", "DOLocationID",
            "tpep_pickup_datetime", "tpep_dropoff_datetime"]
    df = df.dropna(subset=[c for c in core if c in df.columns])

    if "passenger_count" in df.columns:
        median_pax = df["passenger_count"].median()
        df["passenger_count"] = df["passenger_count"].fillna(median_pax)

    fee_cols = [
        "extra", "mta_tax", "tip_amount", "tolls_amount",
        "improvement_surcharge", "congestion_surcharge", "Airport_fee", "cbd_congestion_fee",
    ]
    for col in fee_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    if "RatecodeID" in df.columns:
        mode_rate = df["RatecodeID"].mode()
        fill_rate = int(mode_rate.iloc[0]) if len(mode_rate) else 1
        df["RatecodeID"] = df["RatecodeID"].fillna(fill_rate)

    logger.info("Missing value handling: %d -> %d rows", n_start, len(df))
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 4. Outliers
# ---------------------------------------------------------------------------


def _iqr_mask(series: pd.Series, multiplier: float = 1.5) -> pd.Series:
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
    return series.between(lower, upper)


def remove_outliers(df: pd.DataFrame, cfg: TLCConfig) -> pd.DataFrame:
    """
    Remove outliers on fare, distance, duration, and implied speed.

    Uses IQR by default; quantile clipping optional for heavy-tailed fare data.
    """
    n_start = len(df)
    df = df.copy()

    duration_sec = (
        df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    ).dt.total_seconds()
    df["_duration_min"] = duration_sec / 60.0
    df["_avg_speed_mph"] = np.where(
        df["_duration_min"] > 0,
        df["trip_distance"] / (df["_duration_min"] / 60.0),
        np.nan,
    )

    # Speed sanity (removes GPS/timer glitches)
    df = df[df["_avg_speed_mph"].between(cfg.min_avg_speed_mph, cfg.max_avg_speed_mph)]

    if cfg.outlier_method == "quantile":
        low, high = cfg.fare_quantile_low, cfg.fare_quantile_high
        for col in ("fare_amount", "trip_distance", "_duration_min"):
            lo, hi = df[col].quantile([low, high])
            df = df[df[col].between(lo, hi)]
    else:
        for col in ("fare_amount", "trip_distance", "_duration_min"):
            df = df[_iqr_mask(df[col], cfg.iqr_multiplier)]

    df = df.drop(columns=["_duration_min", "_avg_speed_mph"], errors="ignore")
    logger.info("Outliers removed: %d -> %d (dropped %d)", n_start, len(df), n_start - len(df))
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 5. Feature engineering
# ---------------------------------------------------------------------------


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create features aligned with real-time fare prediction (no target leakage).

    Avoid using tip_amount, tolls, total_amount as features when predicting fare_amount.
    """
    df = df.copy()
    pickup = df["tpep_pickup_datetime"]
    dropoff = df["tpep_dropoff_datetime"]

    df["trip_duration_min"] = (dropoff - pickup).dt.total_seconds() / 60.0
    df["avg_speed_mph"] = np.where(
        df["trip_duration_min"] > 0,
        df["trip_distance"] / (df["trip_duration_min"] / 60.0),
        0.0,
    )

    df["pickup_hour"] = pickup.dt.hour
    df["pickup_day_of_week"] = pickup.dt.dayofweek  # 0=Monday
    df["pickup_month"] = pickup.dt.month
    df["is_weekend"] = (df["pickup_day_of_week"] >= 5).astype(int)

    # NYC rush hours (weekday morning/evening peaks)
    rush = (
        (df["pickup_day_of_week"] < 5)
        & (
            df["pickup_hour"].between(7, 9)
            | df["pickup_hour"].between(16, 19)
        )
    )
    df["is_rush_hour"] = rush.astype(int)

    df["trip_duration_per_mile"] = np.where(
        df["trip_distance"] > 0,
        df["trip_duration_min"] / df["trip_distance"],
        df["trip_duration_min"],
    )

    # Airport / negotiated fare flags from RatecodeID (TLC standard codes)
    if "RatecodeID" in df.columns:
        df["is_airport_trip"] = df["RatecodeID"].isin([2, 3]).astype(int)
    else:
        df["is_airport_trip"] = 0

    # Same pickup and dropoff zone — short local trip indicator
    df["same_zone_trip"] = (df["PULocationID"] == df["DOLocationID"]).astype(int)

    return df


# ---------------------------------------------------------------------------
# 6. Train / test split
# ---------------------------------------------------------------------------


def split_train_test(
    df: pd.DataFrame,
    cfg: TLCConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Time-based split prevents leakage from future trips into training.

    Uses earliest (1 - test_size) fraction for train, latest for test.
    """
    df = df.sort_values("tpep_pickup_datetime").reset_index(drop=True)

    if cfg.split_strategy == "time":
        cut = int(len(df) * (1 - cfg.test_size))
        train_df = df.iloc[:cut].copy()
        test_df = df.iloc[cut:].copy()
        logger.info(
            "Time split: train %s -> %s | test %s -> %s",
            train_df["tpep_pickup_datetime"].min(),
            train_df["tpep_pickup_datetime"].max(),
            test_df["tpep_pickup_datetime"].min(),
            test_df["tpep_dropoff_datetime"].max(),
        )
    else:
        train_df, test_df = train_test_split(
            df,
            test_size=cfg.test_size,
            random_state=cfg.random_state,
        )
        logger.info("Random split: train=%d test=%d", len(train_df), len(test_df))

    return train_df, test_df


def build_feature_matrices(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cfg: TLCConfig,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Extract X/y for sklearn — only configured model features + target."""
    features = [f for f in cfg.model_features if f in train_df.columns]
    extra = [f for f in ("is_airport_trip", "same_zone_trip") if f in train_df.columns]
    features = list(dict.fromkeys(features + extra))  # preserve order, dedupe

    X_train = train_df[features].copy()
    y_train = train_df[cfg.target_column].copy()
    X_test = test_df[features].copy()
    y_test = test_df[cfg.target_column].copy()
    return X_train, y_train, X_test, y_test


# ---------------------------------------------------------------------------
# 7. Persist
# ---------------------------------------------------------------------------


def save_outputs(
    df: pd.DataFrame,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    cfg: TLCConfig,
    report: dict,
) -> None:
    out = Path(cfg.processed_dir)
    out.mkdir(parents=True, exist_ok=True)

    df.to_parquet(out / "cleaned_full.parquet", index=False)
    train_df.to_parquet(out / "train.parquet", index=False)
    test_df.to_parquet(out / "test.parquet", index=False)
    X_train.to_parquet(out / "X_train.parquet", index=False)
    X_test.to_parquet(out / "X_test.parquet", index=False)
    y_train.to_frame(name=cfg.target_column).to_parquet(out / "y_train.parquet", index=False)
    y_test.to_frame(name=cfg.target_column).to_parquet(out / "y_test.parquet", index=False)

    with open(out / "preparation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info("Saved processed artifacts to %s", out)


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------


def run_pipeline(
    input_path: Path | None = None,
    cfg: TLCConfig | None = None,
    skip_outliers: bool = False,
) -> dict:
    cfg = cfg or DEFAULT_CONFIG
    input_path = Path(input_path or cfg.raw_path)

    raw = load_dataset(input_path)
    raw = normalize_column_names(raw)

    n_raw = len(raw)
    df = remove_invalid_rows(raw, cfg)
    df = handle_missing_values(df, cfg)
    if not skip_outliers:
        df = remove_outliers(df, cfg)
    df = engineer_features(df)

    train_df, test_df = split_train_test(df, cfg)
    X_train, y_train, X_test, y_test = build_feature_matrices(train_df, test_df, cfg)

    report = {
        "input_path": str(input_path),
        "rows_raw": n_raw,
        "rows_cleaned": len(df),
        "rows_train": len(train_df),
        "rows_test": len(test_df),
        "target_column": cfg.target_column,
        "feature_columns": list(X_train.columns),
        "split_strategy": cfg.split_strategy,
        "outlier_removal": not skip_outliers,
        "fare_amount_mean": float(df[cfg.target_column].mean()),
        "fare_amount_std": float(df[cfg.target_column].std()),
    }

    save_outputs(df, train_df, test_df, X_train, y_train, X_test, y_test, cfg, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="NYC TLC data preparation pipeline")
    parser.add_argument("--input", "-i", type=Path, help="Path to Parquet or CSV")
    parser.add_argument("--output-dir", "-o", type=Path, help="Processed output directory")
    parser.add_argument(
        "--split",
        choices=("time", "random"),
        default="time",
        help="Train/test split strategy",
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--no-outlier-removal", action="store_true")
    args = parser.parse_args()

    cfg = TLCConfig(
        raw_path=args.input or DEFAULT_CONFIG.raw_path,
        processed_dir=args.output_dir or DEFAULT_CONFIG.processed_dir,
        split_strategy=args.split,
        test_size=args.test_size,
    )

    report = run_pipeline(
        input_path=cfg.raw_path,
        cfg=cfg,
        skip_outliers=args.no_outlier_removal,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
