export default function PlcPanel({ plc, isRunning }) {
  const download = () => {
    const blob = new Blob([plc.code], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "pid_auto.st";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <span>04 · PLC code (IEC 61131-3 Structured Text)</span>
        {plc && (
          <span className="count">
            {plc.verify.ok ? "verify ok" : "verify failed"}
          </span>
        )}
      </div>

      {!plc && (
        <div className="table-empty">
          {isRunning ? "Generating…" : "The generated PLC code appears here."}
        </div>
      )}

      {plc && (
        <div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
          <pre
            style={{
              margin: 0,
              padding: 12,
              overflow: "auto",
              maxHeight: 360,
              background: "var(--ink-950)",
              border: "1px solid var(--line-600)",
              fontFamily: "var(--font-mono)",
              fontSize: 12,
            }}
          >
            {plc.code}
          </pre>

          {plc.verify.errors.length > 0 && (
            <div className="error-banner">{plc.verify.errors.join(" | ")}</div>
          )}
          {plc.warnings.map((w, i) => (
            <div key={i} style={{ color: "var(--paper-dim)", fontSize: 12 }}>
              {w}
            </div>
          ))}

          <div>
            <button type="button" className="run-button" onClick={download}>
              Download .st file
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
