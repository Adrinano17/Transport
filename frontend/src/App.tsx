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
        <h1>Lagos Fare Predictor</h1>
        <p>Fast, local fare estimates for Lagos trips in Nigerian Naira.</p>
      </header>

      <main>
        <FareForm onSubmit={predict} loading={loading} />
        {loading && <LoadingSpinner />}
        {error && !loading && <ErrorAlert message={error} />}
        {prediction && !loading && <PredictionResult prediction={prediction} />}
      </main>

      <footer>
        <p>Built for Lagos routes, weather, and traffic.</p>
      </footer>
    </div>
  );
}
