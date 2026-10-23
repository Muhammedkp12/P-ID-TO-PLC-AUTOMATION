import { useEffect, useState } from "react";
import UploadPanel from "./components/UploadPanel.jsx";
import ResultViewer from "./components/ResultViewer.jsx";
import DetectionTable from "./components/DetectionTable.jsx";
import { detectSymbols, checkHealth } from "./api/detectApi.js";

export default function App() {
  const [imageUrl, setImageUrl] = useState(null);
  const [result, setResult] = useState(null); // { width, height, detections, filename }
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [backendReady, setBackendReady] = useState(null); // null = unknown

  useEffect(() => {
    checkHealth()
      .then((h) => setBackendReady(!!h.model_loaded))
      .catch(() => setBackendReady(false));
  }, []);

  const runDetection = async (file) => {
    setError(null);
    setIsRunning(true);
    setSelectedIndex(null);

    const localUrl = URL.createObjectURL(file);
    setImageUrl(localUrl);

    try {
      const data = await detectSymbols(file);
      setResult(data);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(detail || "Detection failed. Is the backend running?");
      setResult(null);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark">Lineweight</span>
          <span className="brand-tag">P&amp;ID symbol detection</span>
        </div>
        <div className="header-status">
          <span
            className={`status-dot ${
              isRunning ? "busy" : backendReady ? "ready" : ""
            }`}
          />
          {isRunning
            ? "Processing"
            : backendReady === null
            ? "Checking backend…"
            : backendReady
            ? "Model loaded"
            : "Model unavailable"}
        </div>
      </header>

      <section className="hero">
        <p className="hero-eyebrow">Symbol · tag · confidence</p>
        <h1>
          Read every valve, instrument and <em>tag</em> on the sheet.
        </h1>
        <p>
          Upload a scanned or exported P&amp;ID drawing. A YOLO model finds
          each piping and instrumentation symbol, then OCR reads the tag
          text next to it — turning a static drawing into a structured list
          you can search, export, or feed into a digital twin.
        </p>
      </section>

      <main className="workspace">
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <UploadPanel onRun={runDetection} isRunning={isRunning} error={error} />
          <ResultViewer
            imageUrl={imageUrl}
            width={result?.width}
            height={result?.height}
            detections={result?.detections || []}
            selectedIndex={selectedIndex}
            onSelect={setSelectedIndex}
            isRunning={isRunning}
          />
        </div>

        <DetectionTable
          detections={result?.detections || []}
          selectedIndex={selectedIndex}
          onSelect={setSelectedIndex}
        />
      </main>
    </div>
  );
}
