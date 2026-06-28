"""
Lagos Transportation Dataset Generator — 10,000+ synthetic records.

Usage:
  python generate_dataset.py
  python generate_dataset.py --records 15000 --output ../../data/processed/lagos/lagos_transport.csv
"""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Add src to path when run as script
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent.parent / "src"))

from lagos_fare.application.services.lagos_fare_engine import LagosFareEngine
from lagos_fare.domain.data.lagos_locations import LAGOS_LOCATIONS
from lagos_fare.domain.value_objects.traffic_level import TrafficLevel
from lagos_fare.domain.value_objects.transport_type import TransportType
from lagos_fare.domain.value_objects.weather_condition import WeatherCondition

PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "lagos" / "lagos_transport.csv"

LOCATION_NAMES = [
    "Ikeja", "Yaba", "Lekki", "Ajah", "Ikoyi", "Surulere",
    "Victoria Island", "Oshodi", "Murtala Muhammed Airport",
]

TRANSPORT_TYPES = list(TransportType)
TRAFFIC_LEVELS = list(TrafficLevel)
WEATHER_CONDITIONS = list(WeatherCondition)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    from math import asin, cos, radians, sin, sqrt

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371.0 * 2 * asin(sqrt(a))


def estimate_duration_min(distance_km: float, traffic: TrafficLevel) -> float:
    speed = {"low": 35, "moderate": 25, "heavy": 18, "gridlock": 10}[traffic.value]
    return max((distance_km / speed) * 60, 5.0)


def generate_records(n: int, seed: int = 42) -> pd.DataFrame:
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    engine = LagosFareEngine()

    loc_list = list(LAGOS_LOCATIONS.values())
    rows = []

    for _ in range(n):
        pickup_loc, dropoff_loc = rng.sample(loc_list, 2)
        road_km = haversine_km(
            pickup_loc.latitude, pickup_loc.longitude,
            dropoff_loc.latitude, dropoff_loc.longitude,
        ) * rng.uniform(1.15, 1.45)

        transport = rng.choice(TRANSPORT_TYPES)
        traffic = rng.choices(
            TRAFFIC_LEVELS,
            weights=[0.25, 0.35, 0.30, 0.10],
        )[0]
        weather = rng.choices(
            WEATHER_CONDITIONS,
            weights=[0.45, 0.25, 0.22, 0.08],
        )[0]

        duration = estimate_duration_min(road_km, traffic) * rng.uniform(0.9, 1.2)

        hour = rng.choices(
            list(range(24)),
            weights=[1]*6 + [3]*3 + [2]*4 + [3]*3 + [2]*4 + [1]*4,
        )[0]
        requested_at = datetime(2025, rng.randint(1, 12), rng.randint(1, 28), hour, rng.randint(0, 59))

        breakdown = engine.calculate(
            distance_km=road_km,
            duration_min=duration,
            transport_type=transport,
            traffic=traffic,
            weather=weather,
            requested_at=requested_at.replace(tzinfo=__import__("datetime").timezone.utc),
        )

        # Add realistic noise
        fare = float(breakdown.predicted_fare_ngn) * rng.uniform(0.95, 1.08)

        rows.append({
            "pickup_location": pickup_loc.name,
            "destination": dropoff_loc.name,
            "pickup_lat": pickup_loc.latitude,
            "pickup_lng": pickup_loc.longitude,
            "dropoff_lat": dropoff_loc.latitude,
            "dropoff_lng": dropoff_loc.longitude,
            "distance_km": round(road_km, 2),
            "duration_minutes": round(duration, 1),
            "traffic_level": traffic.value,
            "weather_condition": weather.value,
            "transport_type": transport.value,
            "pickup_hour": hour,
            "is_weekend": int(requested_at.weekday() >= 5),
            "fare_ngn": round(fare, 0),
        })

    return pd.DataFrame(rows)


DATA_DICTIONARY = """# Lagos Transportation Dataset — Data Dictionary

| Field | Type | Description |
|-------|------|-------------|
| pickup_location | string | Origin area name in Lagos |
| destination | string | Destination area name |
| pickup_lat | float | Pickup latitude (WGS84) |
| pickup_lng | float | Pickup longitude |
| dropoff_lat | float | Destination latitude |
| dropoff_lng | float | Destination longitude |
| distance_km | float | Road distance estimate (km) |
| duration_minutes | float | Trip duration (minutes) |
| traffic_level | categorical | low, moderate, heavy, gridlock |
| weather_condition | categorical | sunny, cloudy, rainy, thunderstorm |
| transport_type | categorical | taxi, bolt, uber, keke, brt, danfo |
| pickup_hour | int | Hour of day (0-23) |
| is_weekend | int | 1 if Saturday/Sunday |
| fare_ngn | float | Target fare in Nigerian Naira |
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Lagos transport dataset")
    parser.add_argument("--records", type=int, default=10000)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = generate_records(args.records, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)

    dict_path = args.output.parent / "DATA_DICTIONARY.md"
    dict_path.write_text(DATA_DICTIONARY, encoding="utf-8")

    print(f"Generated {len(df):,} records -> {args.output}")
    print(f"Fare range: NGN {df['fare_ngn'].min():,.0f} - NGN {df['fare_ngn'].max():,.0f}")
    print(f"Mean fare: NGN {df['fare_ngn'].mean():,.0f}")


if __name__ == "__main__":
    main()
