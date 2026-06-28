# Systems Analysis and Design Documentation Package

## Lagos Transport Fare Prediction System Using Machine Learning

**Author:** Systems Analysis Team  
**Version:** 2.0 (Lagos Edition)  
**Date:** June 2026

---

# SECTION 1: USE CASE DIAGRAM

## 1.1 Diagram Explanation

The Use Case Diagram models functional requirements from the perspective of external actors interacting with the Lagos Transport Fare Prediction System. It defines system boundaries and enumerates services the system provides.

## 1.2 Diagram Components

| Actor | Role |
|-------|------|
| **User** | Commuter requesting fare estimates |
| **Administrator** | Generates reports and analytics |
| **OpenRouteService API** | External routing provider |
| **OpenWeatherMap API** | External weather provider |

**Use Cases:** Select Pickup/Destination, Select Transport Type, Request Fare Prediction, View Route/Weather/Fare, Store Prediction, Generate Reports, View Analytics.

## 1.3 Mermaid Code

```mermaid
flowchart LR
    User((User))
    Admin((Administrator))
    ORS[OpenRouteService API]
    OWM[OpenWeatherMap API]

    subgraph System[Lagos Transport Fare Prediction System]
        UC1[Select Pickup Location]
        UC2[Select Destination]
        UC3[Select Transport Type]
        UC4[Request Fare Prediction]
        UC5[View Route Information]
        UC6[View Weather Information]
        UC7[View Predicted Fare]
        UC8[Store Prediction]
        UC9[Generate Reports]
        UC10[View Prediction Analytics]
    end

    User --> UC1 & UC2 & UC3 & UC4
    UC4 --> UC5 & UC6 & UC7
    UC4 --> UC8
    Admin --> UC9 & UC10
    UC4 -.-> ORS
    UC4 -.-> OWM
```

## 1.4 PlantUML Code

```plantuml
@startuml Lagos_UseCase
left to right direction
actor User
actor Administrator as Admin
actor "OpenRouteService API" as ORS
actor "OpenWeatherMap API" as OWM

rectangle "Lagos Transport Fare Prediction System" {
  usecase "Select Pickup Location" as UC1
  usecase "Select Destination" as UC2
  usecase "Select Transport Type" as UC3
  usecase "Request Fare Prediction" as UC4
  usecase "View Route Information" as UC5
  usecase "View Weather Information" as UC6
  usecase "View Predicted Fare" as UC7
  usecase "Store Prediction" as UC8
  usecase "Generate Reports" as UC9
  usecase "View Analytics" as UC10
}

User --> UC1
User --> UC2
User --> UC3
User --> UC4
UC4 ..> UC5 : include
UC4 ..> UC6 : include
UC4 ..> UC7 : include
UC4 --> UC8
Admin --> UC9
Admin --> UC10
UC4 --> ORS
UC4 --> OWM
@enduml
```

## 1.5 Academic Description

The use case model captures the functional scope of the proposed system within the context of Lagos urban mobility. The primary actor (User) initiates fare prediction by specifying origin, destination, and transport mode among Taxi, Bolt, Uber, Keke, BRT, and Danfo. The system orchestrates external API calls as secondary actors, persisting results for subsequent analytical review by the Administrator.

---

# SECTION 2: CONTEXT DIAGRAM

## 2.1 Diagram Explanation

The Context Diagram (Level 0) depicts the system as a single process bounded from its environment, showing data flows between external entities and the central system.

## 2.2 Components

- **User** → trip request → **System** → fare estimate (₦) → **User**
- **Administrator** → report request → **System** → CSV/Excel/charts → **Admin**
- **System** ↔ coordinates → **Route API**
- **System** ↔ coordinates → **Weather API**

## 2.3 Mermaid

```mermaid
flowchart LR
    User([User])
    Admin([Administrator])
    ORS[Route API\nOpenRouteService]
    OWM[Weather API\nOpenWeatherMap]

    SYS[Lagos Transport\nFare Prediction System]

    User -->|pickup, dropoff, transport_type| SYS
    SYS -->|fare_ngn, route, weather| User
    Admin -->|report_request| SYS
    SYS -->|CSV, Excel, PNG| Admin
    SYS <-->|coordinates, distance, duration| ORS
    SYS <-->|coordinates, temp, rain| OWM
```

## 2.4 PlantUML

```plantuml
@startuml Lagos_Context
actor User
actor Administrator
database "Route API" as ORS
database "Weather API" as OWM
rectangle "Lagos Transport Fare Prediction System" as SYS

User --> SYS : trip_request
SYS --> User : fare_estimate_NGN
Administrator --> SYS : analytics_request
SYS --> Administrator : reports_charts
SYS --> ORS : route_query
ORS --> SYS : distance_duration
SYS --> OWM : weather_query
OWM --> SYS : conditions
@enduml
```

## 2.5 Academic Description

At the highest abstraction level, the system functions as an intermediary between commuters and external geospatial/meteorological data providers, transforming heterogeneous inputs into unified fare estimates denominated in Nigerian Naira.

---

# SECTION 3: DATA FLOW DIAGRAMS

## 3A. DFD Level 0

### Mermaid

```mermaid
flowchart LR
    User([User]) -->|trip_details| P0[Lagos Fare\nPrediction System]
    P0 -->|fare_result| User
    P0 <-->|route_data| ORS[ORS API]
    P0 <-->|weather_data| OWM[OWM API]
    P0 -->|prediction_log| DB[(SQLite)]
```

### Academic Description

DFD Level 0 consolidates all internal processing into a single bubble, emphasising external data sources and persistent storage.

## 3B. DFD Level 1

### Mermaid

```mermaid
flowchart TB
    User([User]) -->|1 trip_request| P1[1.0 Validate Input]
    P1 -->|2 validated| P2[2.0 Route Retrieval]
    P1 -->|2 validated| P3[3.0 Weather Retrieval]
    P2 -->|3 route| P4[4.0 Fare Prediction]
    P3 -->|3 weather| P4
    P4 -->|4 fare_ngn| P5[5.0 Result Storage]
    P5 -->|5 stored| DB[(D1 Predictions)]
    P4 -->|4 fare_ngn| User
    P2 <-->|coords| ORS[ORS]
    P3 <-->|coords| OWM[OWM]
```

### Processes

| ID | Process | Input | Output |
|----|---------|-------|--------|
| 1.0 | Validate Input | trip_request | validated_trip |
| 2.0 | Route Retrieval | coordinates | distance_km, duration_min |
| 3.0 | Weather Retrieval | coordinates | temperature, rainfall, condition |
| 4.0 | Fare Prediction | features | fare_ngn |
| 5.0 | Result Storage | prediction | DB record |

## 3C. DFD Level 2 — Fare Prediction (4.0)

```mermaid
flowchart TB
    IN[route + weather + trip] --> P41[4.1 Feature Engineering]
    P41 --> P42[4.2 Traffic Classification]
    P41 --> P43[4.3 Lagos Fare Engine]
    P42 --> P43
    P43 --> P44[4.4 Apply Multipliers]
    P44 --> OUT[fare_ngn + breakdown]
```

---

# SECTION 4: ENTITY RELATIONSHIP DIAGRAM

## 4.1 ERD (3NF)

```mermaid
erDiagram
    LOCATION ||--o{ PREDICTION : pickup
    LOCATION ||--o{ PREDICTION : dropoff

    LOCATION {
        int id PK
        float latitude
        float longitude
        string label
        string area
        datetime created_at
    }

    PREDICTION {
        string id PK
        int pickup_location_id FK
        int dropoff_location_id FK
        string pickup_label
        string dropoff_label
        float distance_km
        float duration_min
        string traffic_level
        string transport_type
        string weather_condition
        float predicted_fare
        string currency
        datetime created_at
    }
```

## 4.2 SQL Schema

```sql
CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    label VARCHAR(120),
    area VARCHAR(80),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE predictions (
    id VARCHAR(36) PRIMARY KEY,
    pickup_location_id INTEGER NOT NULL REFERENCES locations(id),
    dropoff_location_id INTEGER NOT NULL REFERENCES locations(id),
    pickup_label VARCHAR(120),
    dropoff_label VARCHAR(120),
    distance_km REAL NOT NULL,
    duration_min REAL NOT NULL,
    traffic_level VARCHAR(20) NOT NULL,
    transport_type VARCHAR(20) NOT NULL,
    weather_condition VARCHAR(40) NOT NULL,
    predicted_fare REAL NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    model_version VARCHAR(64) NOT NULL,
    features_json TEXT NOT NULL,
    requested_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4.3 Academic Description

The schema normalises location data to eliminate redundancy while denormalising weather and route attributes within predictions for analytical query performance.

---

# SECTION 5: CLASS DIAGRAM

```mermaid
classDiagram
    class PredictFareUseCase {
        +execute(dto) FarePredictionDTO
    }
    class LagosFareEngine {
        +calculate() FareBreakdown
    }
    class RouteProvider {
        <<interface>>
        +get_route() RouteInfo
    }
    class WeatherProvider {
        <<interface>>
        +get_weather() WeatherInfo
    }
    class PredictionRepository {
        <<interface>>
        +save()
        +list_recent()
    }
    class OpenRouteServiceClient
    class OpenWeatherMapClient
    class SqlitePredictionRepository
    class ReportingService
    class AnalyticsService

    PredictFareUseCase --> LagosFareEngine
    PredictFareUseCase --> RouteProvider
    PredictFareUseCase --> WeatherProvider
    PredictFareUseCase --> PredictionRepository
    OpenRouteServiceClient ..|> RouteProvider
    OpenWeatherMapClient ..|> WeatherProvider
    SqlitePredictionRepository ..|> PredictionRepository
```

---

# SECTION 6: SEQUENCE DIAGRAM

```mermaid
sequenceDiagram
    actor User
    participant React
    participant API as FastAPI
    participant UC as PredictFareUseCase
    participant ORS as RouteService
    participant OWM as WeatherService
    participant Engine as LagosFareEngine
    participant DB as SQLite

    User->>React: Select Airport→VI, Bolt
    React->>API: POST /predictions
    API->>UC: TripRequestDTO
    UC->>ORS: get_route()
    ORS-->>UC: 24km, 52min
    UC->>OWM: get_weather()
    OWM-->>UC: rainy, 27°C
    UC->>Engine: calculate()
    Engine-->>UC: ₦6,450
    UC->>DB: INSERT prediction
    UC-->>API: FarePredictionDTO
    API-->>React: JSON
    React-->>User: Display ₦6,450
```

---

# SECTION 7: ACTIVITY DIAGRAM

```mermaid
flowchart TD
    Start([Start]) --> Input[Input Route + Transport Type]
    Input --> Validate{Valid Lagos coords?}
    Validate -->|No| Error[Return 400 Error]
    Validate -->|Yes| FetchRoute[Fetch Route Data]
    FetchRoute --> FetchWeather[Fetch Weather Data]
    FetchWeather --> Features[Generate Features]
    Features --> Predict[Predict Fare via Engine]
    Predict --> Save[Save to SQLite]
    Save --> Display[Display Fare in ₦]
    Display --> End([End])
    Error --> End
```

---

# SECTION 8: COMPONENT DIAGRAM

```mermaid
flowchart TB
    subgraph Frontend
        React[React SPA]
    end
    subgraph Backend
        API[FastAPI API Layer]
        UC[Prediction Service]
        RS[Route Service]
        WS[Weather Service]
        FE[Lagos Fare Engine]
        ML[ML Model]
        REP[Reporting Module]
        ANA[Analytics Module]
    end
    DB[(SQLite)]
    ORS[ORS API]
    OWM[OWM API]

    React --> API
    API --> UC
    UC --> RS & WS & FE & ML
    UC --> DB
    REP & ANA --> DB
    RS --> ORS
    WS --> OWM
```

---

# SECTION 9: DEPLOYMENT DIAGRAM

```mermaid
flowchart TB
    Browser[Client Browser]
    Vercel[Vercel\nReact Frontend]
    Render[Render\nFastAPI Backend]
    SQLite[(SQLite File)]
    ORS[OpenRouteService]
    OWM[OpenWeatherMap]

    Browser -->|HTTPS| Vercel
    Browser -->|API calls| Render
    Render --> SQLite
    Render --> ORS
    Render --> OWM
```

---

# SECTION 10: SYSTEM ARCHITECTURE

```mermaid
flowchart TB
    User([Lagos Commuter]) --> FE[React Frontend]
    FE --> API[FastAPI Backend]
    API --> APP[Application Layer\nUse Cases]
    APP --> DOM[Domain Layer\nEntities + Ports]
    APP --> INF[Infrastructure\nORS, OWM, SQLite, sklearn]
    INF --> DB[(SQLite)]
    INF --> ML[Lagos ML Model]
    INF --> EXT[External APIs]
```

---

# SECTION 11: MACHINE LEARNING WORKFLOW

```mermaid
flowchart LR
    A[Data Collection\n10K Lagos records] --> B[Data Cleaning]
    B --> C[Feature Engineering]
    C --> D[Train/Test Split]
    D --> E[Model Training\nLR + RF]
    E --> F[Evaluation\nMAE, RMSE, R², MAPE]
    F --> G[Model Selection]
    G --> H[Deploy joblib]
    H --> I[Live Prediction]
```

---

# SECTION 12: RESEARCH METHODOLOGY

```mermaid
flowchart TD
    P1[Problem Identification] --> P2[Literature Review]
    P2 --> P3[Requirement Gathering]
    P3 --> P4[System Design]
    P4 --> P5[Development\nFastAPI + React]
    P5 --> P6[Testing\n48 test cases]
    P6 --> P7[Evaluation\nMetrics + Charts]
    P7 --> P8[Documentation\nChapters 1-5]
```

---

*End of Systems Analysis and Design Package*
