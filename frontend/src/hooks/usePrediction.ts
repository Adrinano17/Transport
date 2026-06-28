import { useCallback, useState } from "react";
import { parseApiError, predictFare } from "../api/client";
import type { FarePrediction, TripRequest } from "../types/prediction";

interface UsePredictionState {
  prediction: FarePrediction | null;
  loading: boolean;
  error: string | null;
  predict: (request: TripRequest) => Promise<void>;
  reset: () => void;
}

export function usePrediction(): UsePredictionState {
  const [prediction, setPrediction] = useState<FarePrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const predict = useCallback(async (request: TripRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await predictFare(request);
      setPrediction(result);
    } catch (err) {
      setPrediction(null);
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setPrediction(null);
    setError(null);
  }, []);

  return { prediction, loading, error, predict, reset };
}
