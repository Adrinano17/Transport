/** Lagos location coordinates and route presets */

export interface LagosPoint {
  name: string;
  latitude: number;
  longitude: number;
  area?: string;
}

export const LAGOS_LOCATIONS: Record<string, LagosPoint> = {
  murtala_muhammed_airport: { name: "Murtala Muhammed Airport", latitude: 6.5774, longitude: 3.3212, area: "Ikeja" },
  ikeja: { name: "Ikeja", latitude: 6.6018, longitude: 3.3515, area: "Ikeja" },
  yaba: { name: "Yaba", latitude: 6.5158, longitude: 3.3892, area: "Mainland" },
  surulere: { name: "Surulere", latitude: 6.4969, longitude: 3.3550, area: "Mainland" },
  lekki: { name: "Lekki", latitude: 6.4474, longitude: 3.5562, area: "Island" },
  ajah: { name: "Ajah", latitude: 6.4683, longitude: 3.6015, area: "Island" },
  ikoyi: { name: "Ikoyi", latitude: 6.4541, longitude: 3.4350, area: "Island" },
  victoria_island: { name: "Victoria Island", latitude: 6.4281, longitude: 3.4219, area: "Island" },
  maryland: { name: "Maryland", latitude: 6.5783, longitude: 3.3676, area: "Mainland" },
  ojota: { name: "Ojota", latitude: 6.5820, longitude: 3.3880, area: "Mainland" },
  berger: { name: "Berger", latitude: 6.6420, longitude: 3.3430, area: "Mainland" },
  oshodi: { name: "Oshodi", latitude: 6.5489, longitude: 3.3286, area: "Mainland" },
  cms: { name: "CMS (Marina)", latitude: 6.4549, longitude: 3.3886, area: "Island" },
};

export const LAGOS_PRESETS = [
  { id: "airport_vi", label: "Airport → Victoria Island", pickup: "murtala_muhammed_airport", dropoff: "victoria_island" },
  { id: "yaba_lekki", label: "Yaba → Lekki", pickup: "yaba", dropoff: "lekki" },
  { id: "ikeja_ikoyi", label: "Ikeja → Ikoyi", pickup: "ikeja", dropoff: "ikoyi" },
  { id: "berger_cms", label: "Berger → CMS", pickup: "berger", dropoff: "cms" },
  { id: "ajah_vi", label: "Ajah → Victoria Island", pickup: "ajah", dropoff: "victoria_island" },
] as const;

export const TRANSPORT_TYPES = [
  { value: "taxi", label: "Taxi" },
  { value: "bolt", label: "Bolt" },
  { value: "uber", label: "Uber" },
  { value: "keke", label: "Keke (Tricycle)" },
  { value: "brt", label: "BRT Bus" },
  { value: "danfo", label: "Danfo (Bus)" },
] as const;

export const CURRENCY_SYMBOL = "₦";
