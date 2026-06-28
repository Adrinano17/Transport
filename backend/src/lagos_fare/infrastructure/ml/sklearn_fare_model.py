"""SklearnFareModel — loads joblib artifact and predicts fare."""

from __future__ import annotations

import logging
from decimal import Decimal
from pathlib import Path

import joblib
import numpy as np

from lagos_fare.application.exceptions import ModelNotLoadedError
from lagos_fare.domain.ports.fare_model import FareModel
from lagos_fare.domain.value_objects.feature_vector import FeatureVector
from lagos_fare.infrastructure.ml.rule_based_fallback import RuleBasedFallback

logger = logging.getLogger(__name__)


class SklearnFareModel(FareModel):
    def __init__(self, model_path: str | Path) -> None:
        self._path = Path(model_path)
        self._artifact: dict | None = None
        self._fallback = RuleBasedFallback()
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            logger.warning("Model file not found at %s — using rule-based fallback", self._path)
            self._artifact = None
            return
        self._artifact = joblib.load(self._path)
        logger.info("Loaded model: %s", self._artifact.get("model_name", "unknown"))

    @property
    def version(self) -> str:
        if self._artifact:
            return str(self._artifact.get("model_version", "sklearn-v1"))
        return self._fallback.version

    @property
    def feature_names(self) -> tuple[str, ...]:
        if self._artifact:
            return tuple(self._artifact.get("feature_names", ()))
        return self._fallback.feature_names

    @property
    def is_loaded(self) -> bool:
        return self._artifact is not None

    def reload(self) -> None:
        self._load()

    def predict(self, features: FeatureVector) -> Decimal:
        if self._artifact is None:
            return self._fallback.predict(features)

        names = tuple(self._artifact.get("feature_names", ()))
        row = np.array([features.values.get(n, 0.0) for n in names]).reshape(1, -1)
        pipeline = self._artifact["model"]
        pred = float(pipeline.predict(row)[0])
        return Decimal(str(round(max(pred, 2.5), 2)))
