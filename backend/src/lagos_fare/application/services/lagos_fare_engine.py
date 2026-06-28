"""
Lagos Fare Estimation Engine — transportation economist pricing model.

Formula (Nigerian Naira):
    fare = (base_fare + distance_km × per_km + duration_min × per_min)
           × traffic_multiplier × weather_multiplier × time_multiplier

Pricing reflects 2024–2026 Lagos market rates for each transport mode.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

from lagos_fare.domain.value_objects.traffic_level import TrafficLevel
from lagos_fare.domain.value_objects.transport_type import TransportType
from lagos_fare.domain.value_objects.weather_condition import WeatherCondition

LAGOS_TZ = ZoneInfo("Africa/Lagos")

# Nigerian pricing rules — base fare (₦), per km (₦), per minute (₦)
TRANSPORT_RATES: dict[TransportType, tuple[int, int, int]] = {
    TransportType.TAXI: (500, 120, 25),
    TransportType.BOLT: (600, 130, 28),
    TransportType.UBER: (600, 135, 30),
    TransportType.KEKE: (200, 80, 15),
    TransportType.BRT: (100, 35, 5),
    TransportType.DANFO: (150, 50, 8),
}

# Minimum fares by mode (₦)
MINIMUM_FARES: dict[TransportType, int] = {
    TransportType.TAXI: 800,
    TransportType.BOLT: 900,
    TransportType.UBER: 900,
    TransportType.KEKE: 300,
    TransportType.BRT: 200,
    TransportType.DANFO: 250,
}


@dataclass(frozen=True)
class FareBreakdown:
    base_fare_ngn: Decimal
    distance_charge_ngn: Decimal
    duration_charge_ngn: Decimal
    subtotal_ngn: Decimal
    traffic_multiplier: float
    weather_multiplier: float
    time_multiplier: float
    predicted_fare_ngn: Decimal
    transport_type: str
    traffic_level: str
    weather_condition: str


class LagosFareEngine:
    """
    Production fare calculator for Lagos transport modes.

    Time-of-day surcharges align with Third Mainland Bridge / Lekki-Epe
    rush patterns (07:00–10:00, 16:00–20:00 WAT).
    """

    RUSH_HOURS = {7, 8, 9, 16, 17, 18, 19}
    NIGHT_HOURS = {22, 23, 0, 1, 2, 3, 4, 5}

    def calculate(
        self,
        distance_km: float,
        duration_min: float,
        transport_type: TransportType,
        traffic: TrafficLevel,
        weather: WeatherCondition,
        requested_at: datetime,
    ) -> FareBreakdown:
        base, per_km, per_min = TRANSPORT_RATES[transport_type]

        base_dec = Decimal(str(base))
        dist_charge = Decimal(str(round(distance_km * per_km, 2)))
        dur_charge = Decimal(str(round(duration_min * per_min, 2)))
        subtotal = base_dec + dist_charge + dur_charge

        traffic_mult = traffic.multiplier
        weather_mult = weather.multiplier
        time_mult = self._time_multiplier(requested_at, transport_type)

        raw = float(subtotal) * traffic_mult * weather_mult * time_mult
        minimum = MINIMUM_FARES[transport_type]
        final = max(raw, minimum)

        # Round to nearest ₦10 (common Lagos fare rounding)
        final_dec = Decimal(str(final)).quantize(Decimal("10"), rounding=ROUND_HALF_UP)

        return FareBreakdown(
            base_fare_ngn=base_dec,
            distance_charge_ngn=dist_charge,
            duration_charge_ngn=dur_charge,
            subtotal_ngn=subtotal,
            traffic_multiplier=traffic_mult,
            weather_multiplier=weather_mult,
            time_multiplier=time_mult,
            predicted_fare_ngn=final_dec,
            transport_type=transport_type.value,
            traffic_level=traffic.value,
            weather_condition=weather.value,
        )

    def _time_multiplier(self, at: datetime, transport: TransportType) -> float:
        local = at.astimezone(LAGOS_TZ)
        hour = local.hour

        mult = 1.0
        if hour in self.RUSH_HOURS:
            mult *= 1.20
        if hour in self.NIGHT_HOURS and transport in (
            TransportType.TAXI,
            TransportType.BOLT,
            TransportType.UBER,
        ):
            mult *= 1.15
        if local.weekday() >= 5:  # Saturday/Sunday slight premium on Island routes
            mult *= 1.05
        return mult
