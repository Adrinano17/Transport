"""
NYC TLC Yellow Taxi — Exploratory Data Analysis (EDA).

Produces visualizations and summary statistics for fare prediction:
  - Fare distribution (raw vs log)
  - Feature relationships (distance, duration, time)
  - Correlation heatmap
  - Outlier detection (boxplots + IQR counts)
  - Temporal patterns (hour, DOW, month)

Usage:
  python eda.py --input ../../data/processed/nyc_tlc/cleaned_full.parquet
  python eda.py --input ../../data/raw/nyc_tlc/yellow_tripdata.parquet --prepare-first

Outputs saved to data/reports/nyc_tlc/eda/
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import DEFAULT_CONFIG, TLCConfig
from prepare_data import engineer_features, handle_missing_values, load_dataset, remove_invalid_rows

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Plot style — readable defaults for reports
sns.set_theme(style="whitegrid", palette="husl", font_scale=1.05)
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.bbox"] = "tight"


def ensure_output_dir(cfg: TLCConfig) -> Path:
    out = Path(cfg.eda_output_dir)
    out.mkdir(parents=True, exist_ok=True)
    return out


def load_for_eda(path: Path, cfg: TLCConfig, prepare_first: bool) -> pd.DataFrame:
    """Load cleaned parquet or run light prep on raw file."""
    df = load_dataset(path)
    if prepare_first or "trip_duration_min" not in df.columns:
        df = remove_invalid_rows(df, cfg)
        df = handle_missing_values(df, cfg)
        df = engineer_features(df)
    if cfg.eda_sample_size and len(df) > cfg.eda_sample_size:
        df = df.sample(n=cfg.eda_sample_size, random_state=cfg.random_state)
        logger.info("EDA sample: %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# EDA sections
# ---------------------------------------------------------------------------


def eda_summary_stats(df: pd.DataFrame, cfg: TLCConfig, out_dir: Path) -> None:
    """Numeric summary + missingness table."""
    numeric = df.select_dtypes(include=[np.number])
    summary = numeric.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).T
    summary.to_csv(out_dir / "summary_statistics.csv")

    missing = df.isnull().sum().sort_values(ascending=False)
    missing = missing[missing > 0]
    if len(missing):
        missing.to_csv(out_dir / "missing_values.csv")
    logger.info("Wrote summary_statistics.csv")


def plot_fare_distribution(df: pd.DataFrame, cfg: TLCConfig, out_dir: Path) -> None:
    """
    Fare is right-skewed — show histogram + KDE on raw and log1p scale.
    Log transform insight: many models behave better on log-fare; helps spot skew.
    """
    target = cfg.target_column
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    sns.histplot(df[target], bins=80, kde=True, ax=axes[0], color="steelblue")
    axes[0].set_title("Fare distribution (USD)")
    axes[0].set_xlabel("fare_amount")

    sns.histplot(np.log1p(df[target]), bins=80, kde=True, ax=axes[1], color="darkorange")
    axes[1].set_title("Log(1 + fare) distribution")
    axes[1].set_xlabel("log1p(fare_amount)")

    # ECDF — proportion of trips below each fare level
    sorted_fare = np.sort(df[target].values)
    ecdf = np.arange(1, len(sorted_fare) + 1) / len(sorted_fare)
    axes[2].plot(sorted_fare, ecdf, color="green")
    axes[2].set_title("Fare ECDF")
    axes[2].set_xlabel("fare_amount")
    axes[2].set_ylabel("Cumulative proportion")
    axes[2].axvline(df[target].median(), color="red", ls="--", label=f"median={df[target].median():.2f}")
    axes[2].legend()

    fig.suptitle("Fare distribution analysis", fontsize=14, y=1.02)
    fig.savefig(out_dir / "01_fare_distribution.png")
    plt.close(fig)


def plot_feature_relationships(df: pd.DataFrame, cfg: TLCConfig, out_dir: Path) -> None:
    """
    Key predictors of fare: trip_distance (strongest), duration, passengers.
    Scatter + regression line reveals linearity assumptions for baseline models.
    """
    target = cfg.target_column
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    sns.scatterplot(
        data=df, x="trip_distance", y=target, alpha=0.15, s=8, ax=axes[0, 0],
    )
    sns.regplot(
        data=df.sample(min(5000, len(df)), random_state=42),
        x="trip_distance", y=target, scatter=False, color="crimson", ax=axes[0, 0],
    )
    axes[0, 0].set_title("Fare vs trip distance")

    if "trip_duration_min" in df.columns:
        sns.scatterplot(
            data=df, x="trip_duration_min", y=target, alpha=0.15, s=8, ax=axes[0, 1],
        )
        axes[0, 1].set_title("Fare vs trip duration (min)")
        axes[0, 1].set_xlim(0, df["trip_duration_min"].quantile(0.99))

    sns.boxplot(data=df, x="passenger_count", y=target, ax=axes[1, 0])
    axes[1, 0].set_title("Fare by passenger count")

    if "pickup_hour" in df.columns:
        hourly = df.groupby("pickup_hour")[target].mean().reset_index()
        sns.lineplot(data=hourly, x="pickup_hour", y=target, marker="o", ax=axes[1, 1])
        axes[1, 1].set_title("Mean fare by pickup hour")
        axes[1, 1].set_xticks(range(0, 24, 2))

    fig.tight_layout()
    fig.savefig(out_dir / "02_feature_relationships.png")
    plt.close(fig)


def plot_correlation_analysis(df: pd.DataFrame, cfg: TLCConfig, out_dir: Path) -> None:
    """
    Pearson correlation among numeric features.
    High |r| with fare_amount confirms feature importance; multicollinearity among
    distance/duration/speed informs feature selection for linear models.
    """
    cols = [
        cfg.target_column, "trip_distance", "trip_duration_min", "avg_speed_mph",
        "passenger_count", "pickup_hour", "pickup_day_of_week", "pickup_month",
        "is_weekend", "is_rush_hour", "trip_duration_per_mile", "total_amount",
    ]
    cols = [c for c in cols if c in df.columns]
    corr = df[cols].corr(numeric_only=True)

    corr.to_csv(out_dir / "correlation_matrix.csv")

    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        ax=ax,
    )
    ax.set_title("Feature correlation matrix (Pearson)")
    fig.savefig(out_dir / "03_correlation_heatmap.png")
    plt.close(fig)

    # Bar chart: correlation with target
    target_corr = corr[cfg.target_column].drop(cfg.target_column).sort_values(key=abs, ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#2ecc71" if v > 0 else "#e74c3c" for v in target_corr.values]
    target_corr.plot(kind="barh", ax=ax, color=colors)
    ax.set_title(f"Correlation with {cfg.target_column}")
    ax.set_xlabel("Pearson r")
    fig.savefig(out_dir / "04_target_correlations.png")
    plt.close(fig)


def plot_outlier_detection(df: pd.DataFrame, cfg: TLCConfig, out_dir: Path) -> None:
    """
    Boxplots + IQR flag counts for fare, distance, duration.
    Documents how many rows the prep pipeline will drop at outlier step.
    """
    metrics = [cfg.target_column, "trip_distance"]
    if "trip_duration_min" in df.columns:
        metrics.append("trip_duration_min")

    fig, axes = plt.subplots(1, len(metrics), figsize=(4 * len(metrics), 5))
    if len(metrics) == 1:
        axes = [axes]

    iqr_report = []
    for ax, col in zip(axes, metrics):
        sns.boxplot(y=df[col], ax=ax, color="skyblue")
        ax.set_title(f"Boxplot: {col}")

        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - cfg.iqr_multiplier * iqr, q3 + cfg.iqr_multiplier * iqr
        n_out = ((df[col] < lower) | (df[col] > upper)).sum()
        iqr_report.append({
            "column": col,
            "q1": q1,
            "q3": q3,
            "iqr_lower": lower,
            "iqr_upper": upper,
            "outlier_count": int(n_out),
            "outlier_pct": round(100 * n_out / len(df), 2),
        })

    pd.DataFrame(iqr_report).to_csv(out_dir / "outlier_iqr_report.csv", index=False)

    fig.suptitle(f"Outlier detection (IQR × {cfg.iqr_multiplier})", y=1.02)
    fig.savefig(out_dir / "05_outlier_boxplots.png")
    plt.close(fig)

    # Z-score scatter for fare vs distance — highlight extreme points
    if "trip_distance" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 6))
        z_fare = (df[cfg.target_column] - df[cfg.target_column].mean()) / df[cfg.target_column].std()
        z_dist = (df["trip_distance"] - df["trip_distance"].mean()) / df["trip_distance"].std()
        extreme = (np.abs(z_fare) > 3) | (np.abs(z_dist) > 3)
        ax.scatter(
            df.loc[~extreme, "trip_distance"],
            df.loc[~extreme, cfg.target_column],
            alpha=0.1, s=6, c="gray", label="normal",
        )
        ax.scatter(
            df.loc[extreme, "trip_distance"],
            df.loc[extreme, cfg.target_column],
            alpha=0.6, s=20, c="red", label=f"|z|>3 (n={extreme.sum()})",
        )
        ax.set_xlabel("trip_distance")
        ax.set_ylabel(cfg.target_column)
        ax.set_title("Outlier highlight: |z-score| > 3")
        ax.legend()
        fig.savefig(out_dir / "06_outlier_scatter_zscore.png")
        plt.close(fig)


def plot_temporal_patterns(df: pd.DataFrame, cfg: TLCConfig, out_dir: Path) -> None:
    """Demand and fare patterns by hour, day of week, month."""
    target = cfg.target_column
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    if "pickup_hour" in df.columns:
        g = df.groupby("pickup_hour").agg(trip_count=(target, "count"), mean_fare=(target, "mean"))
        ax1 = axes[0, 0]
        ax1.bar(g.index, g["trip_count"], alpha=0.6, label="trip count")
        ax1.set_xlabel("Hour of day")
        ax1.set_ylabel("Trip count")
        ax2 = ax1.twinx()
        ax2.plot(g.index, g["mean_fare"], color="crimson", marker="o", label="mean fare")
        ax2.set_ylabel("Mean fare (USD)")
        axes[0, 0].set_title("Trips and mean fare by hour")

    if "pickup_day_of_week" in df.columns:
        dow_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        sns.boxplot(data=df, x="pickup_day_of_week", y=target, ax=axes[0, 1])
        axes[0, 1].set_xticks(range(7))
        axes[0, 1].set_xticklabels(dow_labels)
        axes[0, 1].set_title("Fare by day of week")

    if "pickup_month" in df.columns:
        sns.lineplot(
            data=df.groupby("pickup_month")[target].mean().reset_index(),
            x="pickup_month", y=target, marker="o", ax=axes[1, 0],
        )
        axes[1, 0].set_title("Mean fare by month")
        axes[1, 0].set_xticks(range(1, 13))

    if "is_rush_hour" in df.columns:
        sns.violinplot(data=df, x="is_rush_hour", y=target, ax=axes[1, 1], order=[0, 1])
        axes[1, 1].set_xticks([0, 1])
        axes[1, 1].set_xticklabels(["Off-peak", "Rush hour"])
        axes[1, 1].set_title("Fare: rush hour vs off-peak")

    fig.tight_layout()
    fig.savefig(out_dir / "07_temporal_patterns.png")
    plt.close(fig)


def plot_location_effects(df: pd.DataFrame, cfg: TLCConfig, out_dir: Path) -> None:
    """Top pickup zones by volume and mean fare — location is a strong fare driver."""
    target = cfg.target_column
    if "PULocationID" not in df.columns:
        return

    top_zones = df["PULocationID"].value_counts().head(15).index
    subset = df[df["PULocationID"].isin(top_zones)]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    zone_vol = subset.groupby("PULocationID").size().sort_values(ascending=True)
    zone_vol.plot(kind="barh", ax=axes[0], color="teal")
    axes[0].set_title("Top 15 pickup zones by trip volume")
    axes[0].set_xlabel("Trip count")

    zone_fare = subset.groupby("PULocationID")[target].mean().sort_values(ascending=True)
    zone_fare.plot(kind="barh", ax=axes[1], color="coral")
    axes[1].set_title("Mean fare in top pickup zones")
    axes[1].set_xlabel("Mean fare (USD)")

    fig.tight_layout()
    fig.savefig(out_dir / "08_location_effects.png")
    plt.close(fig)


def run_eda(
    input_path: Path,
    cfg: TLCConfig | None = None,
    prepare_first: bool = False,
) -> Path:
    cfg = cfg or DEFAULT_CONFIG
    out_dir = ensure_output_dir(cfg)
    df = load_for_eda(input_path, cfg, prepare_first)

    logger.info("Running EDA on %d rows", len(df))
    eda_summary_stats(df, cfg, out_dir)
    plot_fare_distribution(df, cfg, out_dir)
    plot_feature_relationships(df, cfg, out_dir)
    plot_correlation_analysis(df, cfg, out_dir)
    plot_outlier_detection(df, cfg, out_dir)
    plot_temporal_patterns(df, cfg, out_dir)
    plot_location_effects(df, cfg, out_dir)

    # EDA plan checklist (markdown)
    plan = r"""# NYC TLC Fare Prediction — EDA Plan

## Objectives
1. Understand fare distribution shape (skew, long tail)
2. Identify primary drivers: distance, duration, time, location
3. Quantify missing data and invalid records
4. Detect outliers before modeling
5. Inform feature engineering and train/test split strategy

## Visualizations produced
| File | Purpose |
|------|---------|
| 01_fare_distribution.png | Histogram, log-fare, ECDF |
| 02_feature_relationships.png | Distance/duration/passengers vs fare |
| 03_correlation_heatmap.png | Multicollinearity check |
| 04_target_correlations.png | Feature ranking by |r| with fare |
| 05_outlier_boxplots.png | IQR-based outlier counts |
| 06_outlier_scatter_zscore.png | Joint fare-distance extremes |
| 07_temporal_patterns.png | Hourly, DOW, monthly, rush hour |
| 08_location_effects.png | Top TLC zones |

## Key hypotheses to validate
- fare_amount ~ trip_distance (expect r > 0.9)
- Rush hour increases fare via duration (traffic proxy)
- Airport rate codes show fare premium
- Log-transform may stabilize variance for linear models

## Next steps after EDA
1. Run prepare_data.py with IQR outlier removal
2. Train baseline: LinearRegression on distance only
3. Train full model: RandomForest / GradientBoosting
4. Compare MAE on hold-out time slice
"""
    (out_dir / "EDA_PLAN.md").write_text(plan, encoding="utf-8")
    logger.info("EDA complete. Reports saved to %s", out_dir)
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="NYC TLC EDA")
    parser.add_argument("--input", "-i", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, help="EDA figure output directory")
    parser.add_argument(
        "--prepare-first",
        action="store_true",
        help="Run validation + feature engineering before EDA (for raw files)",
    )
    parser.add_argument("--sample", type=int, default=100_000, help="Max rows for plotting")
    args = parser.parse_args()

    cfg = TLCConfig(
        eda_output_dir=args.output_dir or DEFAULT_CONFIG.eda_output_dir,
        eda_sample_size=args.sample,
    )
    run_eda(args.input, cfg, prepare_first=args.prepare_first)


if __name__ == "__main__":
    main()
