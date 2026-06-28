"""
NYC TLC Taxi — shared configuration for data prep and EDA.

Supports Yellow Taxi Parquet/CSV (2020+ schema). Adjust COLUMN_MAP if your
file uses legacy names (e.g. tpep_* vs lpep_* for green cabs).
"""

from dataclasses import dataclass, field
from pathlib import Path

# Project root: Transport/
PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "nyc_tlc"
DEFAULT_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "nyc_tlc"
DEFAULT_EDA_DIR = PROJECT_ROOT / "data" / "reports" / "nyc_tlc" / "eda"


@dataclass(frozen=True)
class TLCConfig:
    """Thresholds and paths — tune for your sample size and business rules."""

    raw_path: Path = DEFAULT_RAW_DIR / "yellow_tripdata.parquet"
    processed_dir: Path = DEFAULT_PROCESSED_DIR
    eda_output_dir: Path = DEFAULT_EDA_DIR

    # Target column for fare prediction
    target_column: str = "fare_amount"

    # NYC TLC published valid ranges (approximate, widely used in Kaggle solutions)
    min_fare: float = 2.50
    max_fare: float = 500.0
    min_distance: float = 0.0
    max_distance: float = 100.0  # miles; trips above are often errors
    min_passengers: int = 0
    max_passengers: int = 6
    max_trip_duration_hours: float = 5.0
    min_avg_speed_mph: float = 1.0
    max_avg_speed_mph: float = 80.0

    # Outlier method: "iqr" or "quantile"
    outlier_method: str = "iqr"
    iqr_multiplier: float = 1.5
    fare_quantile_low: float = 0.001
    fare_quantile_high: float = 0.999

    # Train/test
    test_size: float = 0.2
    random_state: int = 42
    # "time" = split by pickup datetime (recommended); "random" = sklearn shuffle
    split_strategy: str = "time"

    # Sampling for EDA on huge files (None = use full dataframe after cleaning)
    eda_sample_size: int | None = 100_000

    # Columns expected in Yellow Taxi 2023+ Parquet
    required_columns: tuple[str, ...] = (
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "PULocationID",
        "DOLocationID",
        "fare_amount",
        "total_amount",
        "payment_type",
        "RatecodeID",
    )

    # Optional columns used when present
    optional_columns: tuple[str, ...] = (
        "extra",
        "mta_tax",
        "tip_amount",
        "tolls_amount",
        "improvement_surcharge",
        "congestion_surcharge",
        "Airport_fee",
        "cbd_congestion_fee",
        "VendorID",
        "store_and_fwd_flag",
    )

    # Feature columns written to train/test matrices (excluding target)
    model_features: tuple[str, ...] = field(
        default=(
            "trip_distance",
            "trip_duration_min",
            "avg_speed_mph",
            "passenger_count",
            "pickup_hour",
            "pickup_day_of_week",
            "pickup_month",
            "is_weekend",
            "is_rush_hour",
            "PULocationID",
            "DOLocationID",
            "payment_type",
            "RatecodeID",
            "trip_duration_per_mile",
        )
    )


DEFAULT_CONFIG = TLCConfig()
