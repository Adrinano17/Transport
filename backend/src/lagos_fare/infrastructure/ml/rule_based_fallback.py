"""Rule-based fare estimate when ML model is unavailable."""

from decimal import Decimal

from lagos_fare.domain.ports.fare_model import FareModel
from lagos_fare.domain.value_objects.feature_vector import FeatureVector


class RuleBasedFallback(FareModel):
    BASE_FARE = Decimal("2.50")
    PER_MILE = Decimal("2.50")
    PER_MIN = Decimal("0.50")

    @property
    def version(self) -> str:
        return "rule-based-v1"

    @property
    def feature_names(self) -> tuple[str, ...]:
        return ("trip_distance", "trip_duration_min", "is_rush_hour")

    def predict(self, features: FeatureVector) -> Decimal:
        v = features.values
        miles = Decimal(str(v.get("trip_distance", v.get("distance_km", 0) * 0.621371)))
        minutes = Decimal(str(v.get("trip_duration_min", v.get("duration_min", 0))))
        rush_mult = Decimal("1.15") if v.get("is_rush_hour", 0) else Decimal("1.0")
        fare = (self.BASE_FARE + miles * self.PER_MILE + minutes * self.PER_MIN) * rush_mult
        rain = Decimal(str(v.get("precipitation_mm", 0)))
        if rain > 0:
            fare += Decimal("1.00")
        return fare.quantize(Decimal("0.01"))
