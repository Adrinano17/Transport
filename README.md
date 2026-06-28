# Lagos Transport Fare Prediction System

Predict transportation fares in **Lagos, Nigeria** using the Lagos Fare Estimation Engine, machine learning, OpenRouteService routing, and OpenWeatherMap weather data. All fares in **Nigerian Naira (₦)**.

## Supported Locations

Ikeja · Yaba · Lekki · Ajah · Ikoyi · Victoria Island · Surulere · Oshodi · Berger · Ojota · Maryland · CMS · Murtala Muhammed Airport

## Transport Types

Taxi · Bolt · Uber · Keke · BRT · Danfo

## Quick Start

```powershell
# 1. Generate Lagos dataset (10,000 records)
cd backend
python scripts\lagos\generate_dataset.py

# 2. Evaluate ML models
python scripts\lagos\run_evaluation.py --data ..\data\processed\lagos\lagos_transport.csv

# 3. Backend
pip install -r requirements.txt
python -m uvicorn lagos_fare.main:app --reload --app-dir src

# 4. Frontend
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/predictions` | Predict fare (₦) |
| POST | `/api/v1/weather` | Weather at coordinates |
| GET | `/api/v1/locations` | Lagos presets |
| GET | `/api/v1/admin/predictions` | Prediction history |
| POST | `/api/v1/admin/reports/generate` | Export CSV/Excel reports |
| POST | `/api/v1/admin/analytics/generate` | Generate PNG charts |

## Lagos Fare Formula

```
fare = (base + distance_km × per_km + duration_min × per_min)
       × traffic_mult × weather_mult × time_mult
```

## Documentation

- [Complete Project Report](docs/FINAL_YEAR_PROJECT_REPORT.md)
- [Chapter 4 Results](docs/CHAPTER_4_RESULTS.md)
- [Systems Analysis & Design](docs/SYSTEMS_ANALYSIS_AND_DESIGN.md)
- [Testing Guide](docs/TESTING.md)

## Testing

```powershell
cd backend && pytest tests/ -v
cd frontend && npm test
```
