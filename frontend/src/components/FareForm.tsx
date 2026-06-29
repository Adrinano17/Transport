import { FormEvent, useMemo, useState } from "react";
import { LAGOS_LOCATIONS, LAGOS_PRESETS, TRANSPORT_TYPES } from "../constants/lagos";
import type { TransportType, TripRequest } from "../types/prediction";

interface FareFormProps {
  onSubmit: (request: TripRequest) => void;
  loading: boolean;
}

export function FareForm({ onSubmit, loading }: FareFormProps) {
  const defaultPickup = LAGOS_LOCATIONS.murtala_muhammed_airport;
  const defaultDropoff = LAGOS_LOCATIONS.victoria_island;

  const [pickupKey, setPickupKey] = useState("murtala_muhammed_airport");
  const [dropoffKey, setDropoffKey] = useState("victoria_island");
  const [pickupLat, setPickupLat] = useState(String(defaultPickup.latitude));
  const [pickupLng, setPickupLng] = useState(String(defaultPickup.longitude));
  const [pickupLabel, setPickupLabel] = useState(defaultPickup.name);
  const [dropoffLat, setDropoffLat] = useState(String(defaultDropoff.latitude));
  const [dropoffLng, setDropoffLng] = useState(String(defaultDropoff.longitude));
  const [dropoffLabel, setDropoffLabel] = useState(defaultDropoff.name);
  const [passengers, setPassengers] = useState(1);
  const [transportType, setTransportType] = useState<TransportType>("bolt");

  const locationOptions = useMemo(
    () => Object.entries(LAGOS_LOCATIONS).map(([key, location]) => ({
      key,
      label: `${location.name} ${location.area ? `(${location.area})` : ""}`.trim(),
    })),
    [],
  );

  const applyPreset = (pickupKey: string, dropoffKey: string) => {
    const p = LAGOS_LOCATIONS[pickupKey];
    const d = LAGOS_LOCATIONS[dropoffKey];
    if (!p || !d) return;
    setPickupKey(pickupKey);
    setDropoffKey(dropoffKey);
    setPickupLat(String(p.latitude));
    setPickupLng(String(p.longitude));
    setPickupLabel(p.name);
    setDropoffLat(String(d.latitude));
    setDropoffLng(String(d.longitude));
    setDropoffLabel(d.name);
  };

  const applyLocation = (locationKey: string, isPickup: boolean) => {
    const location = LAGOS_LOCATIONS[locationKey];
    if (!location) return;
    if (isPickup) {
      setPickupKey(locationKey);
      setPickupLat(String(location.latitude));
      setPickupLng(String(location.longitude));
      setPickupLabel(location.name);
    } else {
      setDropoffKey(locationKey);
      setDropoffLat(String(location.latitude));
      setDropoffLng(String(location.longitude));
      setDropoffLabel(location.name);
    }
  };

  const sameCoordinates = pickupLat === dropoffLat && pickupLng === dropoffLng;

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit({
      pickup: {
        latitude: parseFloat(pickupLat),
        longitude: parseFloat(pickupLng),
        label: pickupLabel || undefined,
      },
      dropoff: {
        latitude: parseFloat(dropoffLat),
        longitude: parseFloat(dropoffLng),
        label: dropoffLabel || undefined,
      },
      passenger_count: passengers,
      transport_type: transportType,
    });
  };

  return (
    <form className="fare-form" onSubmit={handleSubmit}>
      <div className="presets">
        {LAGOS_PRESETS.map((preset) => (
          <button
            key={preset.id}
            type="button"
            onClick={() => applyPreset(preset.pickup, preset.dropoff)}
          >
            {preset.label}
          </button>
        ))}
      </div>
      <div className="location-selectors">
        <label className="location-select">
          Pickup
          <select
            value={pickupKey}
            onChange={(e) => applyLocation(e.target.value, true)}
          >
            {locationOptions.map((option) => (
              <option key={option.key} value={option.key}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label className="location-select">
          Dropoff
          <select
            value={dropoffKey}
            onChange={(e) => applyLocation(e.target.value, false)}
          >
            {locationOptions.map((option) => (
              <option key={option.key} value={option.key}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <p className="location-hint">Use a preset route or update the Lagos coordinates below.</p>

      <label className="transport-select">
        Mode
        <select
          value={transportType}
          onChange={(e) => setTransportType(e.target.value as TransportType)}
        >
          {TRANSPORT_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </label>

      <fieldset>
        <legend>Pickup</legend>
        <input
          placeholder="Latitude"
          value={pickupLat}
          onChange={(e) => setPickupLat(e.target.value)}
          required
        />
        <input
          placeholder="Longitude"
          value={pickupLng}
          onChange={(e) => setPickupLng(e.target.value)}
          required
        />
        <input
          placeholder="Area name"
          value={pickupLabel}
          onChange={(e) => setPickupLabel(e.target.value)}
        />
      </fieldset>

      <fieldset>
        <legend>Dropoff</legend>
        <input
          placeholder="Latitude"
          value={dropoffLat}
          onChange={(e) => setDropoffLat(e.target.value)}
          required
        />
        <input
          placeholder="Longitude"
          value={dropoffLng}
          onChange={(e) => setDropoffLng(e.target.value)}
          required
        />
        <input
          placeholder="Area name"
          value={dropoffLabel}
          onChange={(e) => setDropoffLabel(e.target.value)}
        />
      </fieldset>

      {sameCoordinates && (
        <p className="warning">Pickup and destination cannot be the same coordinates.</p>
      )}

      <label className="passengers">
        Passengers
        <input
          type="number"
          min={1}
          max={6}
          value={passengers}
          onChange={(e) => setPassengers(Number(e.target.value))}
        />
      </label>

      <button type="submit" className="predict-btn" disabled={loading || sameCoordinates}>
        {loading ? "Calculating Fare…" : "Predict Fare (₦)"}
      </button>
    </form>
  );
}
