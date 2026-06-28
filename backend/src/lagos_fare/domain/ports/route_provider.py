"""RouteProvider port — driving distance and duration between two points."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from lagos_fare.domain.entities.geo_location import GeoLocation


@dataclass(frozen=True)
class RouteInfo:
    distance_km: float
    duration_min: float


class RouteProvider(ABC):
    @abstractmethod
    async def get_route(self, pickup: GeoLocation, dropoff: GeoLocation) -> RouteInfo:
        """Return driving route metrics; raise ExternalServiceError on failure."""
