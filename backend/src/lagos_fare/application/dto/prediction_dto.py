from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class FareBreakdownDTO(BaseModel):
    base_fare_ngn: Decimal
    distance_charge_ngn: Decimal
    duration_charge_ngn: Decimal
    subtotal_ngn: Decimal
    traffic_multiplier: float
    weather_multiplier: float
    time_multiplier: float


class FarePredictionDTO(BaseModel):
    id: UUID
    predicted_fare_ngn: Decimal = Field(..., description="Fare in Nigerian Naira (₦)")
    currency: str = "NGN"
    distance_km: float
    duration_min: float
    traffic_level: str
    weather_condition: str
    transport_type: str
    model_version: str
    pickup_label: str | None = None
    dropoff_label: str | None = None
    temperature_c: float | None = None
    humidity: float | None = None
    precipitation_mm: float | None = None
    breakdown: FareBreakdownDTO | None = None


class PredictionListDTO(BaseModel):
    items: list[FarePredictionDTO]
    total: int
    page: int
    page_size: int
