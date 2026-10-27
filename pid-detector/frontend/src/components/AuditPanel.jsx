const short = (h) => (h ? `${h.slice(0, 10)}…` : "");

export default function AuditPanel({ records, chain, latestIndex, onVerify }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <span>05 · Audit trail (hash-chained ledger)</span>
        {chain && (
          <span
            className="count"
            style={{ color: chain.valid ? "var(--green)" : "var(--red)" }}
          >
            {chain.valid
              ? `chain valid · ${chain.records} records`
              : `chain broken at record ${chain.broken_at}`}
          </span>
        )}
      </div>

      {records.length === 0 && (
        <div className="table-empty">Each generated program is recorded here.</div>
      )}

      {records.length > 0 && (
        <div className="table-scroll">
          <table className="detection-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Time (UTC)</th>
                <th>User</th>
                <th>Action</th>
                <th>Tags</th>
                <th>Drawing SHA-256</th>
                <th>Code SHA-256</th>
                <th>Previous hash</th>
                <th>Record hash</th>
              </tr>
            </thead>
            <tbody>
              {[...records].reverse().map((r) => (
                <tr key={r.index} className={r.index === latestIndex ? "selected" : ""}>
                  <td>{r.index}</td>
                  <td>{r.timestamp.replace("T", " ").slice(0, 19)}</td>
                  <td>{r.user}</td>
                  <td>{r.action}</td>
                  <td>{r.tags.length}</td>
                  <td title={r.input_sha256}>{short(r.input_sha256)}</td>
                  <td title={r.code_sha256}>{short(r.code_sha256)}</td>
                  <td title={r.prev_hash}>{short(r.prev_hash)}</td>
                  <td title={r.hash}>{short(r.hash)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div style={{ padding: 12 }}>
        <button type="button" className="run-button" onClick={onVerify}>
          Re-verify chain
        </button>
      </div>
    </div>
  );
}
