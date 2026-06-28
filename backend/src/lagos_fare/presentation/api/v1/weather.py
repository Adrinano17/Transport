from fastapi import APIRouter, Depends

from lagos_fare.application.dto.trip_request_dto import WeatherRequestDTO, WeatherResponseDTO
from lagos_fare.dependencies import get_weather_service
from lagos_fare.domain.entities.geo_location import GeoLocation
from lagos_fare.infrastructure.external.openweather_map import OpenWeatherMapClient

router = APIRouter()


@router.post("", response_model=WeatherResponseDTO, summary="Fetch weather for coordinates")
async def fetch_weather(
    body: WeatherRequestDTO,
    weather_client: OpenWeatherMapClient = Depends(get_weather_service),
) -> WeatherResponseDTO:
    loc = GeoLocation(body.latitude, body.longitude)
    info = await weather_client.get_weather(loc)
    return WeatherResponseDTO(
        temperature=info.temperature_c,
        rainfall=info.precipitation_mm,
        humidity=info.humidity,
        weather_condition=info.summary,
    )
