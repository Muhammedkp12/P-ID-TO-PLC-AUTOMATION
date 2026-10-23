import { useState } from "react";
import UploadPanel from "../components/UploadPanel.jsx";
import ResultViewer from "../components/ResultViewer.jsx";
import DetectionTable from "../components/DetectionTable.jsx";
import { detectSymbols } from "../api/detectApi.js";

export default function Detect() {
  const [imageUrl, setImageUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(null);

  const runDetection = async (file) => {
    setError(null);
    setIsRunning(true);
    setSelectedIndex(null);

    setImageUrl(URL.createObjectURL(file));

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
    <section className="section">
      <div className="workspace-head">
        <h2>Try it on your drawing</h2>
        <p>Upload a sheet, run detection and review what was found.</p>
      </div>

      <main className="workspace">
        <div className="workspace-main">
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
    </section>
  );
}