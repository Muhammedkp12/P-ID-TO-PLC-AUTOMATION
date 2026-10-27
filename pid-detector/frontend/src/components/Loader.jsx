export default function Loader({ label = "Working…" }) {
  return (
    <div className="loader" role="status" aria-live="polite">
      <div className="loader-ring" aria-hidden="true" />
      <p>{label}</p>
    </div>
  );
}