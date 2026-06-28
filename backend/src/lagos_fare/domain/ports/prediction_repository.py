from abc import ABC, abstractmethod
from uuid import UUID

from lagos_fare.domain.entities.fare_prediction import FarePrediction
from lagos_fare.domain.entities.trip_request import TripRequest
from lagos_fare.domain.ports.route_provider import RouteInfo
from lagos_fare.domain.ports.weather_provider import WeatherInfo


class PredictionRepository(ABC):
    @abstractmethod
    async def save(
        self,
        prediction: FarePrediction,
        *,
        trip: TripRequest,
        weather: WeatherInfo,
        route: RouteInfo,
        weather_condition: str,
    ) -> None:
        ...

    @abstractmethod
    async def get_by_id(self, prediction_id: UUID) -> dict | None:
        ...

    @abstractmethod
    async def list_recent(self, page: int, page_size: int) -> tuple[list[dict], int]:
        ...

    @abstractmethod
    async def fetch_all_for_analytics(self) -> list[dict]:
        ...
