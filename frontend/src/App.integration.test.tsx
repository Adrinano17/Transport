import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import MockAdapter from "axios-mock-adapter";
import { describe, expect, it } from "vitest";
import App from "./App";
import { api } from "./api/client";

describe("App integration", () => {
  it("shows loading state then fare result after prediction", async () => {
    const mock = new MockAdapter(api);
    // Delay response so loading UI is observable
    mock.onPost("/api/v1/predictions").reply(() => {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve([
            200,
            {
              id: "integration-id",
              predicted_fare_ngn: 6450,
              distance_km: 28.3,
              duration_min: 56.6,
              traffic_level: "heavy",
              weather_summary: "clear sky",
              model_version: "lagos-fare-engine-v1",
              currency: "NGN",
              transport_type: "bolt",
              weather_condition: "clear sky",
              temperature_c: 22,
              humidity: 60,
            },
          ]);
        }, 100);
      });
    });

    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: /predict fare/i }));

    expect(screen.getByRole("button", { name: /predicting/i })).toBeDisabled();

    await waitFor(() => {
      expect(screen.getByText(/₦6,450/)).toBeInTheDocument();
      expect(screen.getByText(/lagos-fare-engine/i)).toBeInTheDocument();
    });

    mock.restore();
  });

  it("displays error alert when API returns 400", async () => {
    const mock = new MockAdapter(api);
    mock.onPost("/api/v1/predictions").reply(400, {
      type: "invalid_coordinates",
      detail: "Pickup coordinates are outside the service area.",
      status: 400,
      title: "Domain error",
    });

    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByRole("button", { name: /predict fare/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
      expect(screen.getByText(/outside the service area/i)).toBeInTheDocument();
    });

    mock.restore();
  });
});
