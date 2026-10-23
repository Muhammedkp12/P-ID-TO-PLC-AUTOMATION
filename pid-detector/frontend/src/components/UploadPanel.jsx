import { useCallback, useRef, useState } from "react";

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/tiff"];

export default function UploadPanel({ onRun, isRunning, error }) {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  const acceptFile = useCallback((f) => {
    if (!f) return;
    if (!ACCEPTED_TYPES.includes(f.type)) return;
    setFile(f);
  }, []);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    acceptFile(e.dataTransfer.files?.[0]);
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <span>01 · Upload drawing</span>
      </div>

      <label
        className={`dropzone${dragging ? " dragging" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <div className="dropzone-corner" aria-hidden="true" />
        <svg
          className="dropzone-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
        >
          <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M12 12V3m0 0L7 8m5-5l5 5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <p className="dropzone-title">Drop a P&amp;ID sheet, or browse</p>
        <p className="dropzone-sub">JPEG, PNG, WEBP or TIFF · scanned or exported drawings</p>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_TYPES.join(",")}
          onChange={(e) => acceptFile(e.target.files?.[0])}
        />
      </label>

      {file && (
        <div className="file-chip">
          <span>{file.name}</span>
          <button type="button" onClick={() => setFile(null)} aria-label="Remove file">
            ×
          </button>
        </div>
      )}

      {error && <div className="error-banner">{error}</div>}

      <button
        type="button"
        className="run-button"
        disabled={!file || isRunning}
        onClick={() => onRun(file)}
      >
        {isRunning ? "Detecting symbols…" : "Run detection"}
      </button>
    </div>
  );
}
