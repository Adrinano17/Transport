-- Transport Fare Prediction — initial schema
-- SQLite compatible

CREATE TABLE IF NOT EXISTS locations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude        REAL NOT NULL,
    longitude       REAL NOT NULL,
    label           VARCHAR(120),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_locations_coords ON locations (latitude, longitude);

CREATE TABLE IF NOT EXISTS predictions (
    id                  VARCHAR(36) PRIMARY KEY,
    pickup_location_id  INTEGER NOT NULL REFERENCES locations(id),
    dropoff_location_id INTEGER NOT NULL REFERENCES locations(id),
    distance_km         REAL NOT NULL,
    duration_min        REAL NOT NULL,
    traffic_level       VARCHAR(16) NOT NULL,
    temperature_c       REAL NOT NULL,
    humidity            REAL NOT NULL,
    precipitation_mm    REAL NOT NULL,
    weather_condition   VARCHAR(120) NOT NULL,
    predicted_fare      REAL NOT NULL,
    model_version       VARCHAR(64) NOT NULL,
    features_json       TEXT NOT NULL,
    requested_at        TIMESTAMP NOT NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions (created_at DESC);
