# Lagos Transportation Dataset — Data Dictionary

| Field | Type | Description |
|-------|------|-------------|
| pickup_location | string | Origin area name in Lagos |
| destination | string | Destination area name |
| pickup_lat | float | Pickup latitude (WGS84) |
| pickup_lng | float | Pickup longitude |
| dropoff_lat | float | Destination latitude |
| dropoff_lng | float | Destination longitude |
| distance_km | float | Road distance estimate (km) |
| duration_minutes | float | Trip duration (minutes) |
| traffic_level | categorical | low, moderate, heavy, gridlock |
| weather_condition | categorical | sunny, cloudy, rainy, thunderstorm |
| transport_type | categorical | taxi, bolt, uber, keke, brt, danfo |
| pickup_hour | int | Hour of day (0-23) |
| is_weekend | int | 1 if Saturday/Sunday |
| fare_ngn | float | Target fare in Nigerian Naira |
