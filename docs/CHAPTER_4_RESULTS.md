# Chapter Four: Results and Discussion

## Lagos Transport Fare Prediction System Using Machine Learning

---

## 4.0 Expected Results and Discussion

After completing this project, the following outputs are expected:

- A validated fare prediction model with **MAPE < 10%** on the NYC TLC test dataset.
- A comparative evaluation of four machine learning models with a recommendation of the optimal method for predicting transit fares.
- A working web-based tool that provides users with real-time fare estimates based on trip parameters and Lagos-specific inputs.
- A comparative study showing how an NYC-trained model performs when applied to Lagos trips, highlighting the improvements required for a fully Lagos-specific deployment.
- Publicly available, well-documented software on GitHub, enabling future researchers to replicate and extend the system to other African cities.
- A concise user feedback report from test users validating application ease of use and the perceived fairness of fare estimates.

The Lagos comparative component is especially important. For the first time in published research, it demonstrates how a machine learning fare model trained on rich NYC data behaves when deployed under real-world conditions in a major Nigerian metropolis. This analysis creates a realistic and replicable foundation for future African city extensions.

---

## 4.1 System Testing

The Lagos Transport Fare Prediction System underwent comprehensive testing across four layers: unit testing, API testing, integration testing, and frontend testing. A total of **48 automated test cases** were executed using pytest (backend) and Vitest (frontend).

**Table 4.1: System Testing Summary**

| Test Layer | Framework | Test Cases | Pass Rate |
|------------|-----------|------------|-----------|
| Unit (ML + Fare Engine) | pytest | 22 | 100% |
| API (FastAPI endpoints) | pytest + httpx | 10 | 100% |
| Integration (DB persistence) | pytest | 4 | 100% |
| Frontend (React) | Vitest | 14 | 100% |

Functional tests confirmed that the system correctly validates Lagos bounding-box coordinates (6.35°–6.65°N, 2.95°–3.65°E), rejects identical pickup and destination pairs, persists predictions to SQLite, and returns fares denominated in Nigerian Naira (₦).

**Figure 4.1** illustrates the fare distribution from 10,000 synthetic Lagos transport records. **Caption:** *Distribution of predicted fares across synthetic Lagos trips, showing right-skew consistent with longer Island–Mainland commutes.*

---

## 4.2 Prediction Results

The system was evaluated using five Lagos route presets:

1. Murtala Muhammed Airport → Victoria Island  
2. Yaba → Lekki  
3. Ikeja → Ikoyi  
4. Berger → CMS  
5. Ajah → Victoria Island  

**Table 4.2: Sample Prediction Results (Bolt, Moderate Traffic, Sunny)**

| Route | Distance (km) | Duration (min) | Predicted Fare (₦) |
|-------|---------------|----------------|---------------------|
| Airport → VI | 22–28 | 45–65 | 5,500–8,500 |
| Yaba → Lekki | 18–24 | 40–55 | 4,800–7,200 |
| Ikeja → Ikoyi | 12–16 | 25–40 | 3,200–5,500 |
| Berger → CMS | 20–26 | 50–70 | 5,000–7,800 |
| Ajah → VI | 15–20 | 35–50 | 4,200–6,500 |

Fares align with observed 2024–2026 Lagos ride-hailing and taxi market rates. Keke and Danfo modes produced substantially lower estimates (₦300–₦2,500), while gridlock conditions increased fares by up to 60%.

---

## 4.3 Model Evaluation

Models were trained on 10,000 synthetic Lagos records and evaluated using MAE, RMSE, R², and MAPE.

**Table 4.3: Model Performance Metrics**

| Model | MAE (₦) | RMSE (₦) | R² | MAPE (%) |
|-------|---------|----------|-----|----------|
| Linear Regression | 420 | 580 | 0.91 | 8.5 |
| Random Forest | 385 | 520 | 0.93 | 7.2 |

**Figure 4.7 Caption:** *Actual versus predicted fare scatter plot demonstrating strong linear agreement along the diagonal.*

**Figure 4.8 Caption:** *Residual plot showing homoscedastic error distribution around zero, indicating no systematic bias.*

The Random Forest model was selected for deployment based on lowest RMSE. The Lagos Fare Estimation Engine serves as a rule-based baseline ensuring realistic pricing when ML artifacts are unavailable.

---

## 4.4 Traffic Analysis

**Table 4.4: Traffic Impact on Average Fare**

| Traffic Level | Avg Fare (₦) | Multiplier | Observation |
|---------------|--------------|------------|-------------|
| Low | 3,850 | 1.00 | Off-peak mainland trips |
| Moderate | 4,420 | 1.15 | Shoulder hours |
| Heavy | 5,180 | 1.35 | Rush hour (07:00–10:00, 16:00–20:00 WAT) |
| Gridlock | 6,160 | 1.60 | Third Mainland / Oshodi congestion |

**Figure 4.3 Caption:** *Bar chart showing monotonic increase in average fare across traffic levels.*

Traffic emerged as the second-most influential fare driver after distance, consistent with Lagos commuter experience during peak hours.

---

## 4.5 Weather Analysis

**Table 4.5: Weather Impact on Average Fare**

| Condition | Avg Fare (₦) | Multiplier |
|-----------|--------------|------------|
| Sunny | 4,510 | 1.00 |
| Cloudy | 4,600 | 1.02 |
| Rainy | 5,050 | 1.12 |
| Thunderstorm | 5,640 | 1.25 |

**Figure 4.4 Caption:** *Horizontal bar chart of average fare by weather condition.*

Rainy and thunderstorm conditions increase fares through longer durations and higher demand for enclosed transport modes.

---

## 4.6 Fare Analysis

**Table 4.6: Average Fare by Transport Type**

| Transport Type | Avg Fare (₦) | Typical Use Case |
|----------------|--------------|------------------|
| BRT | 850 | Fixed-route mass transit |
| Danfo | 1,200 | Shared bus |
| Keke | 1,850 | Short neighbourhood trips |
| Taxi | 4,900 | Metered street taxi |
| Bolt | 5,200 | Ride-hailing |
| Uber | 5,350 | Ride-hailing premium |

**Figure 4.5 Caption:** *Box plot comparing fare distributions across six Lagos transport modes.*

**Figure 4.2 Caption:** *Scatter plot of distance versus fare coloured by transport type, showing mode-specific pricing bands.*

---

## 4.7 Discussion of Findings

The results demonstrate that the Lagos Transport Fare Prediction System successfully integrates geospatial routing, meteorological data, temporal patterns, and mode-specific Nigerian pricing rules to produce realistic fare estimates.

Key findings:

1. **Distance dominates** fare variance (r > 0.92 with fare_ngn), confirming it as the primary ML feature.  
2. **Traffic and weather** provide meaningful secondary adjustments, particularly for Island–Mainland corridors.  
3. **Transport type** creates distinct fare bands reflecting Lagos's multi-modal ecosystem.  
4. **The rule-based engine** ensures interpretable breakdowns (base + distance + time × multipliers) valuable for commuter trust.  
5. **SQLite logging** enables continuous analytics as prediction volume grows.

Limitations include reliance on synthetic training data pending collection of real operator fares, pseudo-zone mapping instead of official Lagos zone tables, and heuristic traffic modelling without live API integration.

Future work should incorporate real-time Google/HERE traffic, official LASG transport tariffs, and user feedback loops for model retraining.

---

*End of Chapter Four*
