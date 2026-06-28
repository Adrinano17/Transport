import { CURRENCY_SYMBOL } from "../constants/lagos";
import type { FarePrediction } from "../types/prediction";

interface Props {
  prediction: FarePrediction;
}

function formatNaira(amount: number): string {
  return `${CURRENCY_SYMBOL}${amount.toLocaleString("en-NG", { maximumFractionDigits: 0 })}`;
}

export function PredictionResult({ prediction }: Props) {
  const fare = Number(prediction.predicted_fare_ngn);

  return (
    <div className="result-card">
      <p className="result-label">Estimated Lagos Fare</p>
      <p className="result-fare">{formatNaira(fare)}</p>
      <p className="result-source">Local Lagos pricing · {prediction.model_version}</p>

      {(prediction.pickup_label || prediction.dropoff_label) && (
        <p className="result-route">
          {prediction.pickup_label ?? "Pickup"} → {prediction.dropoff_label ?? "Destination"}
        </p>
      )}

      <div className="result-grid">
        <div>
          <span>Transport</span>
          <strong className="transport-badge">{prediction.transport_type.toUpperCase()}</strong>
        </div>
        <div>
          <span>Distance</span>
          <strong>{prediction.distance_km.toFixed(2)} km</strong>
        </div>
        <div>
          <span>Duration</span>
          <strong>{prediction.duration_min.toFixed(1)} min</strong>
        </div>
        <div>
          <span>Traffic</span>
          <strong className={`traffic-${prediction.traffic_level}`}>
            {prediction.traffic_level}
          </strong>
        </div>
        <div>
          <span>Weather</span>
          <strong>{prediction.weather_condition ?? prediction.weather_summary}</strong>
        </div>
        {prediction.temperature_c != null && (
          <div>
            <span>Temperature</span>
            <strong>{prediction.temperature_c.toFixed(1)} °C</strong>
          </div>
        )}
        {prediction.breakdown && (
          <div className="breakdown-full">
            <span>Fare Breakdown</span>
            <strong>
              Base {formatNaira(Number(prediction.breakdown.base_fare_ngn))} + Distance{" "}
              {formatNaira(Number(prediction.breakdown.distance_charge_ngn))} + Time{" "}
              {formatNaira(Number(prediction.breakdown.duration_charge_ngn))}
            </strong>
          </div>
        )}
      </div>
    </div>
  );
}
