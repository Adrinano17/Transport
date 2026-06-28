# Lagos Fare Prediction Report Summary

## Dataset Statistics

- Dataset: `data/processed/lagos/lagos_transport.csv`
- Records: 10,000
- Fare range: ₦226 – ₦36,597
- Mean fare: ₦4,711.73
- Median fare: ₦3,395.50
- Average distance: 19.25 km
- Median distance: 17.77 km
- Average duration: 57.81 minutes

### Transport mode distribution

- taxi: 1,719
- danfo: 1,703
- keke: 1,662
- brt: 1,651
- bolt: 1,647
- uber: 1,618

### Traffic distribution

- moderate: 3,502
- heavy: 2,991
- low: 2,519
- gridlock: 988

### Weather distribution

- sunny: 4,488
- cloudy: 2,526
- rainy: 2,187
- thunderstorm: 799

---

## Model Comparison

| Model | MAE (₦) | RMSE (₦) | R² | MAPE |
|---|---|---|---|---|
| Linear Regression | 1,389 | 1,935 | 0.7524 | 51.6% |
| Random Forest | 322 | 526 | 0.9817 | 7.2% |

Best model: `random_forest`

---

## Charts and artifacts

### Analytics charts

- Fare distribution: `backend/data/reports/lagos/analytics/01_fare_distribution.png`
- Distance vs Fare: `backend/data/reports/lagos/analytics/02_distance_vs_fare.png`
- Traffic impact: `backend/data/reports/lagos/analytics/03_traffic_impact.png`
- Weather impact: `backend/data/reports/lagos/analytics/04_weather_impact.png`
- Transport comparison: `backend/data/reports/lagos/analytics/05_transport_comparison.png`
- Prediction volume: `backend/data/reports/lagos/analytics/06_prediction_volume.png`

### Evaluation charts

- Actual vs Predicted: `backend/data/reports/lagos/evaluation/07_actual_vs_predicted.png`
- Residual plot: `backend/data/reports/lagos/evaluation/08_residual_plot.png`

### Evaluation tables

- Model metrics CSV: `backend/data/reports/lagos/evaluation/metrics_table.csv`
- Model metrics Excel: `backend/data/reports/lagos/evaluation/metrics_table.xlsx`
- Performance summary: `backend/data/reports/lagos/evaluation/model_performance_summary.md`
- Model metrics JSON: `backend/data/reports/lagos/evaluation/model_metrics.json`

---

## Notes

- Screenshots are not available in the repository.
- The report is based on the Lagos synthetic dataset and generated analytics/evaluation outputs.
