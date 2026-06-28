"""FeatureVector — ML feature dict aligned with trained model columns."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FeatureVector:
    """Ordered feature values matching joblib artifact feature_names."""

    values: dict[str, float] = field(default_factory=dict)
    feature_names: tuple[str, ...] = ()

    def to_model_array(self) -> list[float]:
        if self.feature_names:
            return [float(self.values[name]) for name in self.feature_names]
        return [float(v) for v in self.values.values()]
