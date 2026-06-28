"""SQLAlchemy ORM — Lagos Transport Fare Prediction."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class LocationORM(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    label: Mapped[str | None] = mapped_column(String(120))
    area: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    pickup_predictions: Mapped[list["PredictionORM"]] = relationship(
        back_populates="pickup_location",
        foreign_keys="PredictionORM.pickup_location_id",
    )
    dropoff_predictions: Mapped[list["PredictionORM"]] = relationship(
        back_populates="dropoff_location",
        foreign_keys="PredictionORM.dropoff_location_id",
    )


class PredictionORM(Base):
    """Every fare prediction is logged for analytics and dissertation reporting."""

    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    pickup_location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    dropoff_location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)

    pickup_label: Mapped[str | None] = mapped_column(String(120))
    dropoff_label: Mapped[str | None] = mapped_column(String(120))

    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    duration_min: Mapped[float] = mapped_column(Float, nullable=False)
    traffic_level: Mapped[str] = mapped_column(String(20), nullable=False)
    transport_type: Mapped[str] = mapped_column(String(20), nullable=False, default="bolt")

    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)
    precipitation_mm: Mapped[float] = mapped_column(Float, nullable=False)
    weather_condition: Mapped[str] = mapped_column(String(40), nullable=False)

    predicted_fare: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    features_json: Mapped[str] = mapped_column(Text, nullable=False)

    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    pickup_location: Mapped[LocationORM] = relationship(
        back_populates="pickup_predictions",
        foreign_keys=[pickup_location_id],
    )
    dropoff_location: Mapped[LocationORM] = relationship(
        back_populates="dropoff_predictions",
        foreign_keys=[dropoff_location_id],
    )
