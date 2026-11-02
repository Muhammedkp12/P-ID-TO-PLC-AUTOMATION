import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

function CopyField({ label, value }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard?.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };
  return (
    <div className="blk-field">
      <div className="blk-label">{label}</div>
      <div className="blk-value">
        <code>{value}</code>
        <button type="button" className="blk-copy" onClick={copy}>
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
    </div>
  );
}

export default function AuditDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setData(null);
    setError("");
    fetch(`${API}/audit-block/${id}`)
      .then(async (r) => {
        if (!r.ok) throw new Error(r.status === 404 ? "Block not found." : "Could not load the block.");
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(e.message || "Cannot reach the server."));
  }, [id]);

  if (error) {
    return (
      <section className="section">
        <h2>{error}</h2>
        <Link className="blk-back" to="/detect">← Back to the audit trail</Link>
      </section>
    );
  }
  if (!data) return <section className="section"><p>Loading block…</p></section>;

  const { record: r, content_valid, link_valid, total, prev_index, next_index } = data;
  const ok = content_valid && link_valid;

  return (
    <section className="section">
      <Link className="blk-back" to="/detect">← Back to the audit trail</Link>
      <div className="blk-card">
        <div className="blk-head">
          <div>
            <div className="blk-kicker">Block {r.index} of {total - 1}</div>
            <h2>Audit block #{r.index}</h2>
            <div className="blk-time">{r.timestamp}</div>
          </div>
          <span className={`blk-badge ${ok ? "ok" : "bad"}`}>
            {ok ? "✓ Block valid" : "✗ Block tampered"}
          </span>
        </div>

        <div className="blk-grid">
          <div className="blk-field"><div className="blk-label">User</div><div className="blk-plain">{r.user}</div></div>
          <div className="blk-field"><div className="blk-label">Action</div><div className="blk-plain">{r.action}</div></div>
          <div className="blk-field"><div className="blk-label">Tags</div><div className="blk-plain">{(r.tags || []).length}</div></div>
        </div>

        <CopyField label="Drawing SHA-256" value={r.input_sha256} />
        <CopyField label="PLC code SHA-256" value={r.code_sha256} />
        <CopyField label="Previous hash" value={r.prev_hash} />
        <CopyField label="Record hash" value={r.hash} />

        <div className="blk-section-label">Tags in this block</div>
        <div className="blk-tags">
          {(r.tags || []).map((t) => <span key={t} className="blk-tag">{t}</span>)}
        </div>

        <div className="blk-checks">
          <span className={content_valid ? "ok" : "bad"}>
            {content_valid ? "✓" : "✗"} Record hash matches its content
          </span>
          <span className={link_valid ? "ok" : "bad"}>
            {link_valid ? "✓" : "✗"} Previous hash matches the block before it
          </span>
        </div>

        <div className="blk-chain">
          {prev_index !== null
            ? <Link className="blk-link" to={`/audit/${prev_index}`}>← Block #{prev_index}</Link>
            : <span className="blk-link off">Genesis block</span>}
          <span className="blk-link current">#{r.index}</span>
          {next_index !== null
            ? <Link className="blk-link" to={`/audit/${next_index}`}>Block #{next_index} →</Link>
            : <span className="blk-link off">Latest block</span>}
        </div>
      </div>
    </section>
  );
}