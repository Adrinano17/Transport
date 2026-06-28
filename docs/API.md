# API Documentation

> Auto-generated OpenAPI is the source of truth at runtime: `/docs` (Swagger) and `/redoc`.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

v0.1: none (local development). Production should add API key or JWT on admin routes.

---

## POST /predictions

Predict fare for a trip in Lagos.

### Request body

```json
{
  "pickup": { "latitude": 6.5244, "longitude": 3.3792, "label": "Victoria Island" },
  "dropoff": { "latitude": 6.4654, "longitude": 3.4064, "label": "Lekki" },
  "requested_at": "2026-06-03T08:30:00+01:00"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pickup` | GeoPoint | yes | Pickup coordinates (WGS84) |
| `dropoff` | GeoPoint | yes | Dropoff coordinates |
| `requested_at` | ISO 8601 datetime | no | Defaults to now (Africa/Lagos) |

### Response 200

```json
{
  "id": "uuid",
  "predicted_fare_ngn": 2850.50,
  "distance_km": 12.4,
  "duration_min": 38.2,
  "traffic_level": "high",
  "weather_summary": "light rain",
  "model_version": "rf-v1.0.0",
  "breakdown": {
    "base": 2000,
    "traffic_multiplier": 1.15,
    "weather_adjustment": 50
  }
}
```

### Errors

| Status | `type` | When |
|--------|--------|------|
| 422 | `validation_error` | Invalid JSON, out-of-Lagos bbox |
| 400 | `domain_error` | Same pickup and dropoff |
| 502 | `external_service_error` | ORS/OWM unreachable |
| 503 | `service_unavailable` | Model not loaded |

---

## GET /predictions

List prediction history.

### Query parameters

| Param | Default | Description |
|-------|---------|-------------|
| `page` | 1 | Page number |
| `page_size` | 20 | Max 100 |

### Response 200

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

---

## GET /predictions/{id}

Fetch one prediction by id.

### Response 404

Prediction not found.

---

## GET /health

Liveness probe.

```json
{ "status": "ok" }
```

---

## GET /health/ready

Readiness: database reachable and model artifact loaded.

```json
{
  "status": "ready",
  "database": "ok",
  "model": "ok",
  "model_version": "rf-v1.0.0"
}
```

---

## Headers

| Header | Description |
|--------|-------------|
| `X-Request-ID` | Correlation id (echoed on response) |
| `X-Model-Version` | Model used for prediction (on POST /predictions) |
