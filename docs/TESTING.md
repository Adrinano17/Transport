# Testing Guide — Transportation Fare Prediction System

## Overview

| Layer | Framework | Location |
|-------|-----------|----------|
| Backend unit | pytest | `backend/tests/unit/` |
| Backend API | pytest + httpx | `backend/tests/api/` |
| Backend integration | pytest + SQLite | `backend/tests/integration/` |
| Frontend unit/integration | Vitest + Testing Library | `frontend/src/**/*.test.ts(x)` |

## Test case matrix

### ML model (`tests/unit/test_ml_model.py`)

| ID | Test case | Expected |
|----|-----------|----------|
| ML-01 | Rule-based base fare | Correct USD calculation |
| ML-02 | Rush hour multiplier | 1.15× applied |
| ML-03 | Rain surcharge | +$1.00 when precipitation > 0 |
| ML-04 | Sklearn loads joblib artifact | `is_loaded=True`, version set |
| ML-05 | Minimum fare floor | fare ≥ $2.50 |
| ML-06 | Missing model file | Falls back to rule-based |
| ML-07 | Model reload | Picks up new artifact |
| ML-08 | Feature column order | Matches training artifact |

### Application services (`tests/unit/test_feature_builder.py`)

| ID | Test case | Expected |
|----|-----------|----------|
| FB-01 | All 16 TLC features built | Keys present |
| FB-02 | km → miles conversion | Correct ratio |
| FB-03 | Rush hour flag | 1.0 on weekday 8 AM ET |
| FB-04 | Weekend flag | 1.0 on Saturday |
| FB-05 | Pseudo zone deterministic | Same lat/lng → same zone |
| TR-01 | Rush hour traffic | HIGH at 8 AM |
| TR-02 | Midday traffic | LOW at 2 PM |

### Use case (`tests/unit/test_predict_fare_use_case.py`)

| ID | Test case | Expected |
|----|-----------|----------|
| UC-01 | Valid trip | Returns fare + route + weather |
| UC-02 | Out-of-bounds pickup | `InvalidCoordinatesError` |
| UC-03 | Same pickup/dropoff | `SameLocationError` |
| UC-04 | Weather API failure | Neutral defaults, prediction succeeds |

### API (`tests/api/`)

| ID | Endpoint | Test case | Status |
|----|----------|-----------|--------|
| API-01 | GET /health | Liveness | 200 |
| API-02 | GET /health/ready | Model loaded | 200 |
| API-03 | POST /predictions | Valid payload | 200 + fare |
| API-04 | POST /predictions | Missing pickup | 422 |
| API-05 | POST /predictions | Invalid latitude | 422 |
| API-06 | POST /predictions | Out of service area | 400 |
| API-07 | POST /predictions | Same location | 400 |
| API-08 | POST /predictions | passenger_count=99 | 422 |
| API-09 | POST /weather | Valid coords | 200 |
| API-10 | POST /weather | Invalid coords | 422 |

### Integration (`tests/integration/test_prediction_flow.py`)

| ID | Test case | Expected |
|----|-----------|----------|
| INT-01 | Full flow persists prediction | Row in `predictions` table |
| INT-02 | Locations created | 2 rows in `locations` |
| INT-03 | Repeated requests | Separate prediction IDs |
| INT-04 | Route provider called once | `call_count == 1` |

### Frontend (`frontend/src/`)

| ID | Test case | Expected |
|----|-----------|----------|
| FE-01 | parseApiError detail | Extracts `detail` field |
| FE-02 | parseApiError validation | Formats `errors[]` |
| FE-03 | predictFare success | Returns typed response |
| FE-04 | usePrediction loading | loading=true during request |
| FE-05 | usePrediction error | error set on 400 |
| FE-06 | usePrediction reset | Clears state |
| FE-07 | FareForm render | Pickup/destination visible |
| FE-08 | FareForm submit | onSubmit called with coords |
| FE-09 | FareForm preset | JFK coords applied |
| FE-10 | App integration success | Shows $46.39 fare card |
| FE-11 | App integration error | Shows alert on 400 |

## Run tests

### Backend

```powershell
cd backend
pip install -r requirements.txt
pytest tests/ -v --tb=short
```

### Frontend

```powershell
cd frontend
npm install
npm test
```

### Coverage (optional)

```powershell
cd backend
pip install pytest-cov
pytest tests/ --cov=lagos_fare --cov-report=term-missing
```

## CI recommendation

```yaml
# .github/workflows/test.yml
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ -v
        working-directory: .

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: npm ci && npm test
        working-directory: frontend
```
