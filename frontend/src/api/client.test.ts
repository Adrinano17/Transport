import MockAdapter from "axios-mock-adapter";
import { describe, expect, it } from "vitest";
import { api, parseApiError, predictFare } from "./client";

describe("parseApiError", () => {
  it("extracts detail from API error response", () => {
    const mock = new MockAdapter(api);
    mock.onPost("/api/v1/predictions").reply(400, {
      type: "same_location",
      title: "Domain error",
      status: 400,
      detail: "Pickup and dropoff cannot be the same.",
    });

    return predictFare({
      pickup: { latitude: 40.64, longitude: -73.78 },
      dropoff: { latitude: 40.64, longitude: -73.78 },
    }).catch((err) => {
      expect(parseApiError(err)).toBe("Pickup and dropoff cannot be the same.");
      mock.restore();
    });
  });

  it("formats validation errors array when detail absent", () => {
    const mock = new MockAdapter(api);
    mock.onPost("/api/v1/predictions").reply(422, {
      type: "validation_error",
      title: "Invalid request",
      status: 422,
      errors: [{ field: "body.pickup.latitude", message: "Input should be less than or equal to 90" }],
    });

    return predictFare({
      pickup: { latitude: 999, longitude: -73.78 },
      dropoff: { latitude: 40.76, longitude: -73.99 },
    }).catch((err) => {
      expect(parseApiError(err)).toContain("body.pickup.latitude");
      mock.restore();
    });
  });

  it("returns message for generic Error", () => {
    expect(parseApiError(new Error("Network down"))).toBe("Network down");
  });
});

describe("predictFare", () => {
  it("returns prediction on successful API call", async () => {
    const mock = new MockAdapter(api);
    const response = {
      id: "test-uuid",
      predicted_fare_ngn: 42.5,
      distance_km: 18.5,
      duration_min: 35.0,
      traffic_level: "high",
      weather_summary: "clear sky",
      model_version: "linear_regression-test",
      weather_condition: "clear sky",
    };
    mock.onPost("/api/v1/predictions").reply(200, response);

    const result = await predictFare({
      pickup: { latitude: 40.6413, longitude: -73.7781, label: "JFK" },
      dropoff: { latitude: 40.758, longitude: -73.9855, label: "Times Square" },
    });

    expect(result.predicted_fare_ngn).toBe(42.5);
    expect(result.model_version).toBe("linear_regression-test");
    mock.restore();
  });
});
