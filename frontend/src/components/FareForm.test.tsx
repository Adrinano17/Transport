import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { FareForm } from "./FareForm";

describe("FareForm", () => {
  it("renders pickup and destination fields", () => {
    render(<FareForm onSubmit={vi.fn()} loading={false} />);
    expect(screen.getByText("Pickup")).toBeInTheDocument();
    expect(screen.getByText("Destination")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /predict fare/i })).toBeInTheDocument();
  });

  it("disables submit button while loading", () => {
    render(<FareForm onSubmit={vi.fn()} loading={true} />);
    expect(screen.getByRole("button", { name: /predicting/i })).toBeDisabled();
  });

  it("calls onSubmit with parsed coordinates", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<FareForm onSubmit={onSubmit} loading={false} />);

    await user.click(screen.getByRole("button", { name: /predict fare/i }));

    expect(onSubmit).toHaveBeenCalledOnce();
    const payload = onSubmit.mock.calls[0][0];
    expect(payload.pickup.latitude).toBeCloseTo(6.5774);
    expect(payload.dropoff.latitude).toBeCloseTo(6.4281);
    expect(payload.transport_type).toBe("bolt");
    expect(payload.passenger_count).toBe(1);
  });

  it("applies JFK preset when preset button clicked", async () => {
    const user = userEvent.setup();
    render(<FareForm onSubmit={vi.fn()} loading={false} />);

    await user.click(screen.getByRole("button", { name: /airport → victoria island/i }));

    const latInputs = screen.getAllByPlaceholderText("Latitude");
    expect(latInputs[0]).toHaveValue("6.5774");
    expect(latInputs[1]).toHaveValue("6.4281");
  });
});
