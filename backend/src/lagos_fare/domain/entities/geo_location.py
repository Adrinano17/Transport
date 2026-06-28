"""GeoLocation entity — WGS84 point with optional human-readable label."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeoLocation:
    latitude: float
    longitude: float
    label: str | None = None
