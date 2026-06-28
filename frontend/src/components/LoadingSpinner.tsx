export function LoadingSpinner() {
  return (
    <div className="loading" aria-live="polite">
      <div className="spinner" />
      <p>Fetching Lagos route, weather, and fare estimate…</p>
    </div>
  );
}
