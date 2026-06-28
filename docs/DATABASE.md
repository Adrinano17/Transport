# Transport Fare Prediction — Database Design

## ER Diagram

```mermaid
erDiagram
    locations {
        INTEGER id PK
        REAL latitude
        REAL longitude
        VARCHAR label
        TIMESTAMP created_at
    }

    predictions {
        VARCHAR id PK
        INTEGER pickup_location_id FK
        INTEGER dropoff_location_id FK
        REAL distance_km
        REAL duration_min
        VARCHAR traffic_level
        REAL temperature_c
        REAL humidity
        REAL precipitation_mm
        VARCHAR weather_condition
        REAL predicted_fare
        VARCHAR model_version
        TEXT features_json
        TIMESTAMP requested_at
        TIMESTAMP created_at
    }

    locations ||--o{ predictions : "pickup"
    locations ||--o{ predictions : "dropoff"
```

## SQL Schema

See `backend/src/lagos_fare/infrastructure/db/migrations/001_initial.sql`

## SQLAlchemy Models

See `backend/src/lagos_fare/infrastructure/db/models.py`
