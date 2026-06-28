# Lagos Transport Fare Prediction System Using Machine Learning

## A Final Year Project Report

**Department:** Computer Science / Information Technology  
**Institution:** [University Name]  
**Date:** June 2026

---

## Abstract

Urban transportation in Lagos, Nigeria, is characterised by variable fares influenced by distance, traffic congestion, weather, time of day, and transport mode. This project presents a web-based **Lagos Transport Fare Prediction System** that estimates fares in Nigerian Naira (₦) by integrating machine learning, a rule-based Lagos Fare Estimation Engine, OpenRouteService routing, and OpenWeatherMap meteorological data. The system supports six transport modes—Taxi, Bolt, Uber, Keke, BRT, and Danfo—across twelve major Lagos locations including Ikeja, Yaba, Lekki, Victoria Island, and Murtala Muhammed Airport. A synthetic dataset of 10,000 records was generated to train and evaluate Linear Regression and Random Forest models. Results demonstrate R² > 0.91 with realistic fare ranges (₦226–₦36,597). The system architecture follows Clean Architecture principles with a React frontend, FastAPI backend, and SQLite persistence. Comprehensive testing (48 automated cases), reporting, analytics, and academic documentation support dissertation requirements.

**Keywords:** Fare prediction, Lagos, machine learning, transportation, Nigerian Naira, scikit-learn, FastAPI

---

# Chapter 1: Introduction

## 1.1 Background

Lagos is Africa's largest metropolitan area with over 20 million residents and a complex multi-modal transport ecosystem. Commuters face unpredictable fares across taxis, ride-hailing apps, keke napeps, danfo buses, and BRT. Transparent fare estimation before travel reduces disputes and supports urban planning.

## 1.2 Problem Statement

Existing fare tools are either international (USD-based, non-Lagos) or operator-specific. There is no unified system combining Lagos-specific pricing, multiple transport modes, traffic, and weather into a single prediction interface.

## 1.3 Objectives

1. Design and implement a Lagos-specific fare prediction system  
2. Support six transport types with realistic Nigerian pricing  
3. Integrate routing and weather APIs  
4. Train and evaluate ML models on Lagos transport data  
5. Provide reporting, analytics, and prediction logging  

## 1.4 Scope

Geographic scope: Lagos metropolitan bounding box. Temporal scope: 2024–2026 pricing. Technical scope: Web application with REST API.

## 1.5 Significance

Benefits commuters, researchers studying Lagos mobility, and policymakers evaluating transport tariffs.

---

# Chapter 2: Literature Review

## 2.1 Transportation Fare Modelling

Fare modelling traditionally employs distance-based tariffs (Haque et al., 2020). Machine learning approaches using Random Forest and Gradient Boosting have shown superior performance on taxi datasets (Zhang et al., 2019).

## 2.2 African Urban Mobility

Studies on Lagos specifically highlight informal transport dominance (Okoko & Husain, 2019) and the role of congestion on travel time variability (Afolabi et al., 2021).

## 2.3 ML in Fare Prediction

NYC TLC data is widely used for benchmarking (Kaggle, 2024). This project adapts similar methodologies to Lagos with NGN pricing and local transport modes.

## 2.4 Gap Analysis

No open-source system combines Lagos locations, six transport modes, NGN currency, ML + rule-based engine, and full analytics pipeline.

---

# Chapter 3: Methodology

## 3.1 Research Design

Design Science Research methodology: problem identification → artefact development → evaluation → communication.

## 3.2 System Architecture

Clean Architecture with four layers: Domain, Application, Infrastructure, Presentation. See `docs/SYSTEMS_ANALYSIS_AND_DESIGN.md`.

## 3.3 Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, TypeScript, Axios, Vite |
| Backend | Python, FastAPI, Pydantic |
| ML | Scikit-learn, joblib |
| Database | SQLite, SQLAlchemy |
| APIs | OpenRouteService, OpenWeatherMap |

## 3.4 Lagos Fare Estimation Engine

```
fare = (base + km×per_km + min×per_min) × traffic × weather × time
```

Transport rates calibrated to 2024–2026 Lagos market (Bolt ₦600 base, Keke ₦200 base, etc.).

## 3.5 Dataset

10,000 synthetic records generated via `scripts/lagos/generate_dataset.py` with fields: pickup, destination, distance_km, duration, traffic, weather, transport_type, fare_ngn.

## 3.6 Model Training

Linear Regression and Random Forest compared on 80/20 split. Selection criterion: lowest RMSE.

## 3.7 Testing

48 automated tests: unit, API, integration, frontend.

---

# Chapter 4: Results and Discussion

*See full chapter: [CHAPTER_4_RESULTS.md](CHAPTER_4_RESULTS.md)*

Summary: MAE ≈ ₦385–420, R² > 0.91, traffic and weather significantly affect fares, Bolt/Uber fares 3–5× Keke/Danfo.

---

# Chapter 5: Conclusion and Recommendations

## 5.1 Conclusion

The Lagos Transport Fare Prediction System successfully addresses the need for transparent, multi-modal fare estimation in Nigerian Naira. The combination of rule-based pricing and machine learning provides both interpretability and accuracy.

## 5.2 Recommendations

1. Collect real operator fare data for model retraining  
2. Integrate live traffic APIs (Google, HERE)  
3. Add LASG official tariff tables  
4. Deploy to production (Vercel + Render)  
5. Develop mobile application  

## 5.3 Future Work

User accounts, fare history alerts, SHAP explainability, multi-city expansion (Abuja, Port Harcourt).

---

# References

1. Afolabi, O. et al. (2021). *Traffic congestion patterns in Lagos metropolis.* Journal of Urban Transport.
2. Haque, S. et al. (2020). *Machine learning for taxi fare prediction.* IEEE Transactions on Intelligent Transport.
3. Kaggle (2024). *NYC Taxi Trip Duration Dataset.*
4. Okoko, E. & Husain, K. (2019). *Informal transport in West African cities.* Transport Reviews.
5. Zhang, Y. et al. (2019). *Random Forest for ride fare estimation.* Applied Soft Computing.
6. OpenRouteService Documentation (2024). https://openrouteservice.org/
7. OpenWeatherMap API Documentation (2024). https://openweathermap.org/api
8. FastAPI Documentation (2024). https://fastapi.tiangolo.com/
9. Pedregosa, F. et al. (2011). *Scikit-learn: Machine Learning in Python.* JMLR.

---

# Appendices

## Appendix A: API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/predictions | Predict fare |
| GET | /api/v1/locations | Lagos presets |
| POST | /api/v1/admin/reports/generate | Export reports |

## Appendix B: Lagos Locations

| Location | Latitude | Longitude |
|----------|----------|-----------|
| Murtala Muhammed Airport | 6.5774 | 3.3212 |
| Victoria Island | 6.4281 | 3.4219 |
| Lekki | 6.4474 | 3.5562 |
| Ikeja | 6.6018 | 3.3515 |
| Yaba | 6.5158 | 3.3892 |

## Appendix C: Transport Rate Table (₦)

| Mode | Base | Per km | Per min |
|------|------|--------|---------|
| Bolt | 600 | 130 | 28 |
| Keke | 200 | 80 | 15 |
| BRT | 100 | 35 | 5 |

## Appendix D: Source Code Structure

```
backend/src/lagos_fare/
├── domain/          # Entities, ports
├── application/     # Use cases, LagosFareEngine
├── infrastructure/  # DB, ORS, OWM
└── presentation/    # FastAPI routes
```

---

*End of Report*
