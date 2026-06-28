"""
PredictFareUseCase — Lagos route + weather + fare engine + persistence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from lagos_fare.application.dto.prediction_dto import FareBreakdownDTO, FarePredictionDTO
from lagos_fare.application.dto.trip_request_dto import TripRequestDTO
from lagos_fare.application.services.feature_builder import FeatureBuilder
from lagos_fare.application.services.lagos_fare_engine import LagosFareEngine
from lagos_fare.application.services.traffic_service import TrafficService
from lagos_fare.config import Settings
from lagos_fare.domain.entities.fare_prediction import FarePrediction
from lagos_fare.domain.entities.geo_location import GeoLocation
from lagos_fare.domain.entities.trip_request import TripRequest
from lagos_fare.domain.exceptions import InvalidCoordinatesError, SameLocationError
from lagos_fare.domain.ports.fare_model import FareModel
from lagos_fare.domain.ports.prediction_repository import PredictionRepository
from lagos_fare.domain.ports.route_provider import RouteProvider
from lagos_fare.domain.ports.weather_provider import WeatherProvider
from lagos_fare.domain.value_objects.weather_condition import WeatherCondition
from lagos_fare.infrastructure.external.openweather_map import OpenWeatherMapClient


class PredictFareUseCase:
    def __init__(
        self,
        route_provider: RouteProvider,
        weather_provider: WeatherProvider,
        fare_model: FareModel,
        repository: PredictionRepository,
        feature_builder: FeatureBuilder,
        traffic_service: TrafficService,
        fare_engine: LagosFareEngine,
        settings: Settings,
    ) -> None:
        self._route = route_provider
        self._weather = weather_provider
        self._model = fare_model
        self._repo = repository
        self._features = feature_builder
        self._traffic = traffic_service
        self._engine = fare_engine
        self._settings = settings

    def _validate_bbox(self, loc: GeoLocation, label: str) -> None:
        s = self._settings
        if not (s.lat_min <= loc.latitude <= s.lat_max and s.lng_min <= loc.longitude <= s.lng_max):
            raise InvalidCoordinatesError(
                f"{label} coordinates ({loc.latitude}, {loc.longitude}) are outside Lagos service area."
            )

    def _to_entity(self, dto: TripRequestDTO) -> TripRequest:
        pickup = GeoLocation(dto.pickup.latitude, dto.pickup.longitude, dto.pickup.label)
        dropoff = GeoLocation(dto.dropoff.latitude, dto.dropoff.longitude, dto.dropoff.label)
        requested_at = dto.requested_at or datetime.now(timezone.utc)
        if requested_at.tzinfo is None:
            requested_at = requested_at.replace(tzinfo=timezone.utc)

        self._validate_bbox(pickup, "Pickup")
        self._validate_bbox(dropoff, "Dropoff")

        if (
            abs(pickup.latitude - dropoff.latitude) < 1e-6
            and abs(pickup.longitude - dropoff.longitude) < 1e-6
        ):
            raise SameLocationError()

        return TripRequest(
            pickup=pickup,
            dropoff=dropoff,
            requested_at=requested_at,
            passenger_count=dto.passenger_count,
            transport_type=dto.transport_type,
        )

    async def execute(self, dto: TripRequestDTO) -> FarePredictionDTO:
        trip = self._to_entity(dto)

        route = await self._route.get_route(trip.pickup, trip.dropoff)
        try:
            weather = await self._weather.get_weather(trip.pickup)
        except Exception:
            weather = OpenWeatherMapClient.NEUTRAL

        weather_cat = WeatherCondition.from_owm_summary(weather.summary, weather.precipitation_mm)
        traffic = self._traffic.get_level(trip.requested_at, route)

        # Lagos Fare Engine — primary calculator (realistic Nigerian pricing)
        breakdown = self._engine.calculate(
            distance_km=route.distance_km,
            duration_min=route.duration_min,
            transport_type=trip.transport_type,
            traffic=traffic,
            weather=weather_cat,
            requested_at=trip.requested_at,
        )

        features = self._features.build(trip, route, weather, traffic, weather_cat)

        prediction = FarePrediction(
            id=uuid4(),
            predicted_fare_ngn=breakdown.predicted_fare_ngn,
            distance_km=route.distance_km,
            duration_min=route.duration_min,
            traffic_level=traffic,
            weather_summary=weather_cat.value,
            model_version="lagos-fare-engine-v1",
            features=features,
            transport_type=trip.transport_type.value,
        )

        await self._repo.save(
            prediction,
            trip=trip,
            weather=weather,
            route=route,
            weather_condition=weather_cat.value,
        )

        return FarePredictionDTO(
            id=prediction.id,
            predicted_fare_ngn=breakdown.predicted_fare_ngn,
            currency=self._settings.currency,
            distance_km=route.distance_km,
            duration_min=route.duration_min,
            traffic_level=traffic.value,
            weather_condition=weather_cat.value,
            transport_type=trip.transport_type.value,
            model_version="lagos-fare-engine-v1",
            pickup_label=trip.pickup.label,
            dropoff_label=trip.dropoff.label,
            temperature_c=weather.temperature_c,
            humidity=weather.humidity,
            precipitation_mm=weather.precipitation_mm,
            breakdown=FareBreakdownDTO(
                base_fare_ngn=breakdown.base_fare_ngn,
                distance_charge_ngn=breakdown.distance_charge_ngn,
                duration_charge_ngn=breakdown.duration_charge_ngn,
                subtotal_ngn=breakdown.subtotal_ngn,
                traffic_multiplier=breakdown.traffic_multiplier,
                weather_multiplier=breakdown.weather_multiplier,
                time_multiplier=breakdown.time_multiplier,
            ),
        )
