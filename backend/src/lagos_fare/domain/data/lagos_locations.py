"""
Lagos, Nigeria — canonical locations with WGS84 coordinates.

Used for validation presets, dataset generation, and UI quick-select.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LagosLocation:
    name: str
    latitude: float
    longitude: float
    area: str


LAGOS_LOCATIONS: dict[str, LagosLocation] = {
    "murtala_muhammed_airport": LagosLocation("Murtala Muhammed Airport", 6.5774, 3.3212, "Ikeja"),
    "ikeja": LagosLocation("Ikeja", 6.6018, 3.3515, "Ikeja"),
    "yaba": LagosLocation("Yaba", 6.5158, 3.3892, "Mainland"),
    "surulere": LagosLocation("Surulere", 6.4969, 3.3550, "Mainland"),
    "lekki": LagosLocation("Lekki", 6.4474, 3.5562, "Island"),
    "ajah": LagosLocation("Ajah", 6.4683, 3.6015, "Island"),
    "ikoyi": LagosLocation("Ikoyi", 6.4541, 3.4350, "Island"),
    "victoria_island": LagosLocation("Victoria Island", 6.4281, 3.4219, "Island"),
    "maryland": LagosLocation("Maryland", 6.5783, 3.3676, "Mainland"),
    "ojota": LagosLocation("Ojota", 6.5820, 3.3880, "Mainland"),
    "berger": LagosLocation("Berger", 6.6420, 3.3430, "Mainland"),
    "oshodi": LagosLocation("Oshodi", 6.5489, 3.3286, "Mainland"),
    "cms": LagosLocation("CMS (Marina)", 6.4549, 3.3886, "Island"),
}

# Popular route presets for UI
LAGOS_ROUTE_PRESETS: list[dict] = [
    {
        "id": "airport_vi",
        "label": "Airport → Victoria Island",
        "pickup": "murtala_muhammed_airport",
        "dropoff": "victoria_island",
    },
    {
        "id": "yaba_lekki",
        "label": "Yaba → Lekki",
        "pickup": "yaba",
        "dropoff": "lekki",
    },
    {
        "id": "ikeja_ikoyi",
        "label": "Ikeja → Ikoyi",
        "pickup": "ikeja",
        "dropoff": "ikoyi",
    },
    {
        "id": "berger_cms",
        "label": "Berger → CMS",
        "pickup": "berger",
        "dropoff": "cms",
    },
    {
        "id": "ajah_vi",
        "label": "Ajah → Victoria Island",
        "pickup": "ajah",
        "dropoff": "victoria_island",
    },
]
