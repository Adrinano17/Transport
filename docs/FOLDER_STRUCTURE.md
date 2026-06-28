# Project Folder Structure

```
Transport/
├── backend/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   ├── README.md
│   ├── src/
│   │   └── lagos_fare/
│   │       ├── __init__.py
│   │       ├── main.py                    # FastAPI app factory
│   │       ├── config.py                  # Settings (pydantic-settings)
│   │       ├── dependencies.py            # DI wiring
│   │       │
│   │       ├── domain/                    # INNERMOST — no framework imports
│   │       │   ├── __init__.py
│   │       │   ├── entities/
│   │       │   │   ├── trip_request.py
│   │       │   │   ├── fare_prediction.py
│   │       │   │   └── geo_location.py
│   │       │   ├── value_objects/
│   │       │   │   ├── feature_vector.py
│   │       │   │   └── traffic_level.py
│   │       │   ├── exceptions.py
│   │       │   └── ports/                 # Interfaces (ABC / Protocol)
│   │       │       ├── route_provider.py
│   │       │       ├── weather_provider.py
│   │       │       ├── fare_model.py
│   │       │       └── prediction_repository.py
│   │       │
│   │       ├── application/               # Use cases
│   │       │   ├── __init__.py
│   │       │   ├── dto/
│   │       │   │   ├── prediction_dto.py
│   │       │   │   └── trip_request_dto.py
│   │       │   ├── services/
│   │       │   │   ├── feature_builder.py
│   │       │   │   └── traffic_service.py
│   │       │   └── use_cases/
│   │       │       ├── predict_fare.py
│   │       │       ├── get_prediction_history.py
│   │       │       └── get_prediction_by_id.py
│   │       │
│   │       ├── infrastructure/            # Adapters
│   │       │   ├── __init__.py
│   │       │   ├── db/
│   │       │   │   ├── database.py
│   │       │   │   ├── models.py          # SQLAlchemy ORM
│   │       │   │   ├── migrations/
│   │       │   │   └── sqlite_prediction_repository.py
│   │       │   ├── external/
│   │       │   │   ├── openroute_service.py
│   │       │   │   ├── openweather_map.py
│   │       │   │   └── http_client.py
│   │       │   └── ml/
│   │       │       ├── sklearn_fare_model.py
│   │       │       └── rule_based_fallback.py
│   │       │
│   │       └── presentation/              # HTTP layer
│   │           ├── __init__.py
│   │           ├── api/
│   │           │   ├── v1/
│   │           │   │   ├── router.py
│   │           │   │   ├── predictions.py
│   │           │   │   └── health.py
│   │           │   └── errors.py          # Exception handlers
│   │           └── schemas/
│   │               ├── prediction.py      # Pydantic request/response
│   │               └── common.py
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   ├── domain/
│   │   │   └── application/
│   │   └── integration/
│   │       └── test_predictions_api.py
│   │
│   ├── scripts/
│   │   ├── train_model.py
│   │   └── generate_synthetic_data.py
│   │
│   └── artifacts/                         # gitignored — trained models
│       └── .gitkeep
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── .env.example
│   ├── README.md
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       │   └── client.ts
│       ├── components/
│       │   ├── FareForm.tsx
│       │   ├── PredictionResult.tsx
│       │   └── PredictionHistory.tsx
│       ├── hooks/
│       │   └── usePrediction.ts
│       └── types/
│           └── prediction.ts
│
├── data/
│   ├── raw/                               # gitignored optional dumps
│   └── processed/
│       └── lagos_fares_synthetic.csv      # generated for MVP
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── FOLDER_STRUCTURE.md
│   └── API.md                             # human-friendly API guide
│
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.web
│   └── docker-compose.yml
│
├── .gitignore
├── .env.example                           # root pointer / shared notes
└── README.md
```

## Import rules (enforce in code review)

1. `domain` → imports nothing from `application`, `infrastructure`, `presentation`.
2. `application` → imports only `domain`.
3. `infrastructure` → imports `domain` (+ libraries).
4. `presentation` → imports `application` + `domain` (DTOs only where needed).
5. `main.py` / `dependencies.py` → wires concrete adapters to use cases.
