"""FareModel port — ML or rule-based fare estimation."""

from abc import ABC, abstractmethod
from decimal import Decimal

from lagos_fare.domain.value_objects.feature_vector import FeatureVector


class FareModel(ABC):
    @property
    @abstractmethod
    def version(self) -> str:
        ...

    @abstractmethod
    def predict(self, features: FeatureVector) -> Decimal:
        """Return predicted fare in NGN."""
