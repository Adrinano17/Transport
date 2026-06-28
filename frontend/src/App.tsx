import { FareForm } from "./components/FareForm";
import { ErrorAlert } from "./components/ErrorAlert";
import { LoadingSpinner } from "./components/LoadingSpinner";
import { PredictionResult } from "./components/PredictionResult";
import { usePrediction } from "./hooks/usePrediction";
import "./App.css";

export default function App() {
  const { prediction, loading, error, predict } = usePrediction();

  return (
    <div className="app">
      <header>
        <h1>Lagos Transport Fare Prediction System</h1>
        <p>
          Predict fares across Lagos in Nigerian Naira using Lagos-specific pricing, traffic, and weather data.
          Estimates are calibrated for Lagos transport modes and not NYC taxi fares.
        </p>
      </header>

      <main>
        <FareForm onSubmit={predict} loading={loading} />
        {loading && <LoadingSpinner />}
        {error && !loading && <ErrorAlert message={error} />}
        {prediction && !loading && <PredictionResult prediction={prediction} />}
      </main>

      <footer>
        <p>Supported areas: Ikeja · Yaba · Lekki · VI · Ikoyi · Ajah · Oshodi · Berger · CMS · Airport</p>
      </footer>
    </div>
  );
}
