function confClass(conf) {
  if (conf >= 0.75) return "";
  if (conf >= 0.5) return "mid";
  return "low";
}

export default function DetectionTable({ detections, selectedIndex, onSelect }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <span>03 · Detection list</span>
        {detections?.length > 0 && <span className="count">{detections.length}</span>}
      </div>

      {(!detections || detections.length === 0) && (
        <div className="table-empty">No detections yet.</div>
      )}

      {detections && detections.length > 0 && (
        <div className="table-scroll">
          <table className="detection-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Symbol</th>
                <th>Tag</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {detections.map((d, i) => (
                <tr
                  key={i}
                  className={i === selectedIndex ? "selected" : ""}
                  onClick={() => onSelect(i)}
                >
                  <td>{String(i + 1).padStart(2, "0")}</td>
                  <td className="class-cell">{d.class.replaceAll("_", " ")}</td>
                  <td className={`tag-cell${d.tag ? "" : " empty"}`}>
                    {d.tag || "unread"}
                  </td>
                  <td>
                    <span className={`conf-bar-track`}>
                      <span
                        className={`conf-bar-fill ${confClass(d.confidence)}`}
                        style={{ width: `${Math.round(d.confidence * 100)}%` }}
                      />
                    </span>
                    {(d.confidence * 100).toFixed(0)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
