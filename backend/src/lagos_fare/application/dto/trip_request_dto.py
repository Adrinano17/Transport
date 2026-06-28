from datetime import datetime

from pydantic import BaseModel, Field

from lagos_fare.domain.value_objects.transport_type import TransportType


class GeoPointDTO(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    label: str | None = Field(None, max_length=120)


class TripRequestDTO(BaseModel):
    pickup: GeoPointDTO
    dropoff: GeoPointDTO
    requested_at: datetime | None = None
    passenger_count: int = Field(1, ge=1, le=6)
    transport_type: TransportType = TransportType.BOLT


class WeatherRequestDTO(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class WeatherResponseDTO(BaseModel):
    temperature: float
    rainfall: float
    humidity: float
    weather_condition: str
