export interface GeoPoint {
  latitude: number;
  longitude: number;
  label?: string;
}

export type TransportType = "taxi" | "bolt" | "uber" | "keke" | "brt" | "danfo";

export interface TripRequest {
  pickup: GeoPoint;
  dropoff: GeoPoint;
  requested_at?: string;
  passenger_count?: number;
  transport_type?: TransportType;
}

export interface FareBreakdown {
  base_fare_ngn: number;
  distance_charge_ngn: number;
  duration_charge_ngn: number;
  subtotal_ngn: number;
  traffic_multiplier: number;
  weather_multiplier: number;
  time_multiplier: number;
}

export interface FarePrediction {
  id: string;
  predicted_fare_ngn: number;
  currency: string;
  distance_km: number;
  duration_min: number;
  traffic_level: string;
  weather_summary?: string;
  weather_condition?: string;
  transport_type: string;
  model_version: string;
  pickup_label?: string;
  dropoff_label?: string;
  temperature_c?: number;
  humidity?: number;
  precipitation_mm?: number;
  breakdown?: FareBreakdown;
}

export interface ApiError {
  type: string;
  title: string;
  status: number;
  detail: string;
  errors?: { field: string; message: string }[];
}
