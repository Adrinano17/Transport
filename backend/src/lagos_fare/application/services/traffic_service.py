"""Lagos traffic heuristic — Third Mainland / Oshodi / Lekki corridor patterns."""

from datetime import datetime
from zoneinfo import ZoneInfo

from lagos_fare.domain.ports.route_provider import RouteInfo
from lagos_fare.domain.value_objects.traffic_level import TrafficLevel

LAGOS_TZ = ZoneInfo("Africa/Lagos")


class TrafficService:
    def __init__(self, timezone: str = "Africa/Lagos") -> None:
        self._tz = ZoneInfo(timezone)

    def get_level(self, at: datetime, route: RouteInfo) -> TrafficLevel:
        local_hour = at.astimezone(self._tz).hour
        weekday = at.astimezone(self._tz).weekday()

        # Morning and evening Lagos rush
        if weekday < 5 and local_hour in (7, 8, 9, 16, 17, 18, 19):
            if route.duration_min > 90:
                return TrafficLevel.GRIDLOCK
            if route.duration_min > 50:
                return TrafficLevel.HEAVY
            return TrafficLevel.HEAVY

        if local_hour in (6, 10, 15, 20):
            return TrafficLevel.MODERATE

        # Long trips suggest congestion even off-peak
        if route.duration_min > 75:
            return TrafficLevel.HEAVY
        if route.duration_min > 45:
            return TrafficLevel.MODERATE

        return TrafficLevel.LOW
