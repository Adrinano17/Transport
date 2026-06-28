import { act, renderHook, waitFor } from "@testing-library/react";
import MockAdapter from "axios-mock-adapter";
import { describe, expect, it } from "vitest";
import { api } from "../api/client";
import { usePrediction } from "./usePrediction";

describe("usePrediction", () => {
  it("starts in idle state", () => {
    const { result } = renderHook(() => usePrediction());
    expect(result.current.loading).toBe(false);
    expect(result.current.prediction).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it("sets loading then prediction on success", async () => {
    const mock = new MockAdapter(api);
    mock.onPost("/api/v1/predictions").reply(200, {
      id: "abc",
      predicted_fare_ngn: 35.0,
      distance_km: 10,
      duration_min: 20,
      traffic_level: "low",
      weather_summary: "clear",
      model_version: "test-v1",
    });

    const { result } = renderHook(() => usePrediction());

    act(() => {
      result.current.predict({
        pickup: { latitude: 40.64, longitude: -73.78 },
        dropoff: { latitude: 40.76, longitude: -73.99 },
      });
    });

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.prediction?.predicted_fare_ngn).toBe(35.0);
      expect(result.current.error).toBeNull();
    });

    mock.restore();
  });

  it("sets error on API failure", async () => {
    const mock = new MockAdapter(api);
    mock.onPost("/api/v1/predictions").reply(400, {
      type: "same_location",
      detail: "Pickup and dropoff cannot be the same.",
      status: 400,
      title: "Domain error",
    });

    const { result } = renderHook(() => usePrediction());

    await act(async () => {
      await result.current.predict({
        pickup: { latitude: 40.64, longitude: -73.78 },
        dropoff: { latitude: 40.64, longitude: -73.78 },
      });
    });

    await waitFor(() => {
      expect(result.current.error).toBe("Pickup and dropoff cannot be the same.");
      expect(result.current.prediction).toBeNull();
    });

    mock.restore();
  });

  it("reset clears prediction and error", async () => {
    const mock = new MockAdapter(api);
    mock.onPost("/api/v1/predictions").reply(200, {
      id: "abc",
      predicted_fare_ngn: 35.0,
      distance_km: 10,
      duration_min: 20,
      traffic_level: "low",
      weather_summary: "clear",
      model_version: "test-v1",
    });

    const { result } = renderHook(() => usePrediction());

    await act(async () => {
      await result.current.predict({
        pickup: { latitude: 40.64, longitude: -73.78 },
        dropoff: { latitude: 40.76, longitude: -73.99 },
      });
    });

    act(() => result.current.reset());

    expect(result.current.prediction).toBeNull();
    expect(result.current.error).toBeNull();
    mock.restore();
  });
});
