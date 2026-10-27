function confClass(conf) {
  if (conf >= 0.75) return "";
  if (conf >= 0.5) return "mid";
  return "low";
}

// Only symbols whose tag was read are listed. `tags` is already filtered.
export default function DetectionTable({ tags, selectedIndex, onSelect }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <span>03 · Tags read by OCR</span>
        {tags.length > 0 && <span className="count">{tags.length}</span>}
      </div>

      {tags.length === 0 && (
        <div className="table-empty">Tags appear here after you upload a drawing.</div>
      )}

      {tags.length > 0 && (
        <div className="table-scroll">
          <table className="detection-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Tag</th>
                <th>OCR confidence</th>
              </tr>
            </thead>
            <tbody>
              {tags.map((d, i) => {
                const c = d.tag_confidence ?? 0;
                return (
                  <tr
                    key={i}
                    className={i === selectedIndex ? "selected" : ""}
                    onClick={() => onSelect(i)}
                  >
                    <td>{String(i + 1).padStart(2, "0")}</td>
                    <td className="tag-cell">{d.tag}</td>
                    <td>
                      <span className="conf-bar-track">
                        <span
                          className={`conf-bar-fill ${confClass(c)}`}
                          style={{ width: `${Math.round(c * 100)}%` }}
                        />
                      </span>
                      {(c * 100).toFixed(0)}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
