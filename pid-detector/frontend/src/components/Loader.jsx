export default function Loader({ label = "Running detection…" }) {
  return (
    <div className="loader" role="status" aria-live="polite">
      <div className="loader-spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
