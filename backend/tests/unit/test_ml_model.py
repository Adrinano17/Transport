"""
Unit tests — ML model layer (SklearnFareModel, RuleBasedFallback).
"""

from decimal import Decimal
from pathlib import Path

import joblib
import numpy as np
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

from lagos_fare.domain.value_objects.feature_vector import FeatureVector
from lagos_fare.infrastructure.ml.rule_based_fallback import RuleBasedFallback
from lagos_fare.infrastructure.ml.sklearn_fare_model import SklearnFareModel
from tests.helpers import FEATURE_NAMES


class TestRuleBasedFallback:
    def test_predict_base_fare_short_trip(self) -> None:
        model = RuleBasedFallback()
        features = FeatureVector(values={
            "trip_distance": 2.0,
            "trip_duration_min": 10.0,
            "is_rush_hour": 0,
            "precipitation_mm": 0,
        })
        fare = model.predict(features)
        # 2.50 + 2*2.50 + 10*0.50 = 12.50
        assert fare == Decimal("12.50")

    def test_predict_rush_hour_multiplier(self) -> None:
        model = RuleBasedFallback()
        features = FeatureVector(values={
            "trip_distance": 2.0,
            "trip_duration_min": 10.0,
            "is_rush_hour": 1,
            "precipitation_mm": 0,
        })
        fare = model.predict(features)
        assert fare == Decimal("14.38")  # 12.50 * 1.15

    def test_predict_rain_surcharge(self) -> None:
        model = RuleBasedFallback()
        features = FeatureVector(values={
            "trip_distance": 2.0,
            "trip_duration_min": 10.0,
            "is_rush_hour": 0,
            "precipitation_mm": 2.0,
        })
        fare = model.predict(features)
        assert fare == Decimal("13.50")

    def test_version_and_feature_names(self) -> None:
        model = RuleBasedFallback()
        assert model.version == "rule-based-v1"
        assert "trip_distance" in model.feature_names


class TestSklearnFareModel:
    def test_loads_artifact_and_predicts(self, model_artifact_path: Path) -> None:
        model = SklearnFareModel(model_artifact_path)
        assert model.is_loaded is True
        assert model.version == "linear_regression-test"
        assert len(model.feature_names) == len(FEATURE_NAMES)

        values = {name: float(i + 1) for i, name in enumerate(FEATURE_NAMES)}
        features = FeatureVector(values=values, feature_names=model.feature_names)
        fare = model.predict(features)
        assert isinstance(fare, Decimal)
        assert fare >= Decimal("2.50")

    def test_minimum_fare_floor(self, model_artifact_path: Path) -> None:
        model = SklearnFareModel(model_artifact_path)
        # Near-zero features may predict below minimum; model enforces floor
        features = FeatureVector(
            values={name: 0.0 for name in FEATURE_NAMES},
            feature_names=model.feature_names,
        )
        fare = model.predict(features)
        assert fare >= Decimal("2.50")

    def test_fallback_when_model_missing(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent.pkl"
        model = SklearnFareModel(missing)
        assert model.is_loaded is False
        assert model.version == "rule-based-v1"

        features = FeatureVector(values={
            "trip_distance": 5.0,
            "trip_duration_min": 15.0,
            "is_rush_hour": 0,
        })
        fare = model.predict(features)
        assert fare > Decimal("0")

    def test_reload_picks_up_new_artifact(self, tmp_path: Path) -> None:
        path = tmp_path / "reload.pkl"
        model = SklearnFareModel(path)
        assert model.is_loaded is False

        pipeline = Pipeline([("model", LinearRegression())])
        X = np.array([[1.0], [2.0], [3.0]])
        pipeline.fit(X, [10.0, 20.0, 30.0])
        joblib.dump({
            "model": pipeline,
            "model_name": "linear_regression",
            "model_version": "reloaded-v1",
            "feature_names": ["trip_distance"],
        }, path)

        model.reload()
        assert model.is_loaded is True
        assert model.version == "reloaded-v1"

    def test_predict_uses_feature_order_from_artifact(self, tmp_path: Path) -> None:
        """Ensures column order matches training — critical for correct inference."""
        path = tmp_path / "ordered.pkl"
        pipeline = Pipeline([("model", LinearRegression())])
        pipeline.fit(np.array([[3.0], [6.0]]), [15.0, 30.0])
        joblib.dump({
            "model": pipeline,
            "model_name": "linear_regression",
            "model_version": "order-test",
            "feature_names": ["trip_distance"],
        }, path)

        model = SklearnFareModel(path)
        features = FeatureVector(
            values={"trip_distance": 4.0, "trip_duration_min": 99.0},
            feature_names=("trip_distance",),
        )
        fare = model.predict(features)
        assert fare == Decimal("20.00")
