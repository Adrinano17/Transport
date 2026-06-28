import axios, { AxiosError } from "axios";
import type { ApiError, FarePrediction, TripRequest } from "../types/prediction";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "";

export const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

export function parseApiError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const ax = err as AxiosError<ApiError>;
    const data = ax.response?.data;
    if (data?.detail) return data.detail;
    if (data?.errors?.length) {
      return data.errors.map((e) => `${e.field}: ${e.message}`).join("; ");
    }
    return ax.message;
  }
  if (err instanceof Error) return err.message;
  return "An unexpected error occurred";
}

export async function predictFare(request: TripRequest): Promise<FarePrediction> {
  const { data } = await api.post<FarePrediction>("/api/v1/predictions", request);
  return data;
}
