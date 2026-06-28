from dataclasses import dataclass
from datetime import datetime

from lagos_fare.domain.entities.geo_location import GeoLocation
from lagos_fare.domain.value_objects.transport_type import TransportType


@dataclass(frozen=True)
class TripRequest:
    pickup: GeoLocation
    dropoff: GeoLocation
    requested_at: datetime
    passenger_count: int = 1
    transport_type: TransportType = TransportType.BOLT
