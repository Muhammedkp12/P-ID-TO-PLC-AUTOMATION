import { useEffect, useMemo, useState } from "react";
import UploadPanel from "../components/UploadPanel.jsx";
import ResultViewer from "../components/ResultViewer.jsx";
import DetectionTable from "../components/DetectionTable.jsx";
import PlcPanel from "../components/PlcPanel.jsx";
import AuditPanel from "../components/AuditPanel.jsx";
import { generatePlc, getAudit, verifyAudit } from "../api/detectApi.js";

export default function Detect() {
  const [imageUrl, setImageUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [records, setRecords] = useState([]);
  const [chain, setChain] = useState(null);

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
    <section className="section">
      <div className="workspace-head">
        <h2>Try it on your drawing</h2>
        <p>Upload a sheet to detect symbols, read tags and generate PLC code.</p>
      </div>

      <main className="workspace">
        <div className="workspace-main">
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

      <div style={{ padding: "24px 0 0", position: "relative", zIndex: 1 }}>
        <AuditPanel
          records={records}
          chain={chain}
          latestIndex={result?.audit?.index}
          onVerify={refreshAudit}
        />
      </div>
    </section>
  );
}