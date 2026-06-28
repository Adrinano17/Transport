"""
Application configuration — Lagos, Nigeria defaults.
"""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Lagos Transport Fare Prediction API"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./lagos_transport.db"
    ors_api_key: str = ""
    owm_api_key: str = ""
    model_path: str = "artifacts/lagos_model.pkl"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    service_timezone: str = "Africa/Lagos"
    currency: str = "NGN"
    currency_symbol: str = "₦"

    # Lagos metropolitan bounding box
    lat_min: float = 6.35
    lat_max: float = 6.65
    lng_min: float = 2.95
    lng_max: float = 3.65

    reports_output_dir: str = "data/reports/lagos"
    analytics_output_dir: str = "data/reports/lagos/analytics"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
