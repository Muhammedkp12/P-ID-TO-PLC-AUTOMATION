import { useEffect, useMemo, useState } from "react";
import UploadPanel from "./components/UploadPanel.jsx";
import ResultViewer from "./components/ResultViewer.jsx";
import DetectionTable from "./components/DetectionTable.jsx";
import PlcPanel from "./components/PlcPanel.jsx";
import AuditPanel from "./components/AuditPanel.jsx";
import { checkHealth, generatePlc, getAudit, verifyAudit } from "./api/detectApi.js";

export default function App() {
  const [imageUrl, setImageUrl] = useState(null);
  const [result, setResult] = useState(null); // full /generate response
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [backendReady, setBackendReady] = useState(null);
  const [records, setRecords] = useState([]);
  const [chain, setChain] = useState(null);

  // Only symbols whose tag was read are shown anywhere in the UI.
  const tags = useMemo(
    () => (result?.detections || []).filter((d) => d.tag),
    [result]
  );

  const refreshAudit = async () => {
    try {
      setRecords(await getAudit());
      setChain(await verifyAudit());
    } catch {
      setChain({ valid: false, records: 0, broken_at: null });
    }
  };

  useEffect(() => {
    checkHealth()
      .then((h) => setBackendReady(!!h.model_loaded))
      .catch(() => setBackendReady(false));
    refreshAudit();
  }, []);

  const runPipeline = async (file) => {
    setError(null);
    setIsRunning(true);
    setSelectedIndex(null);
    setResult(null);
    setImageUrl(URL.createObjectURL(file));
    try {
      setResult(await generatePlc(file));
      await refreshAudit();
    } catch (err) {
      setError(err?.response?.data?.detail || "Processing failed. Is the backend running?");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark">Lineweight</span>
          <span className="brand-tag">P&amp;ID to PLC</span>
        </div>
        <div className="header-status">
          <span
            className={`status-dot ${isRunning ? "busy" : backendReady ? "ready" : ""}`}
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
        <p className="hero-eyebrow">Tag · PLC code · audit trail</p>
        <h1>
          From a P&amp;ID drawing to <em>PLC code</em>, with a record of it.
        </h1>
        <p>
          Upload a P&amp;ID. Symbols are detected, their tags are read by OCR,
          Structured Text is generated, and every run is added to a hash-chained
          audit log.
        </p>
      </section>

      <main className="workspace">
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <UploadPanel onRun={runPipeline} isRunning={isRunning} error={error} />
          <ResultViewer
            imageUrl={imageUrl}
            width={result?.width}
            height={result?.height}
            detections={tags}
            selectedIndex={selectedIndex}
            onSelect={setSelectedIndex}
            isRunning={isRunning}
          />
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <DetectionTable tags={tags} selectedIndex={selectedIndex} onSelect={setSelectedIndex} />
          <PlcPanel plc={result} isRunning={isRunning} />
        </div>
      </main>

      <div style={{ padding: "0 40px 48px", position: "relative", zIndex: 1 }}>
        <AuditPanel
          records={records}
          chain={chain}
          latestIndex={result?.audit?.index}
          onVerify={refreshAudit}
        />
      </div>
    </div>
  );
}
