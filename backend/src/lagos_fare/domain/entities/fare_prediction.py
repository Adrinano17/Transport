from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from lagos_fare.domain.value_objects.feature_vector import FeatureVector
from lagos_fare.domain.value_objects.traffic_level import TrafficLevel


@dataclass(frozen=True)
class FarePrediction:
    id: UUID
    predicted_fare_ngn: Decimal
    distance_km: float
    duration_min: float
    traffic_level: TrafficLevel
    weather_summary: str
    model_version: str
    features: FeatureVector
    transport_type: str = "bolt"
