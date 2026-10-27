"""Hash-chained audit log (simulated ledger).

Each record stores the hash of the previous record, so editing or deleting
any line breaks every hash after it. The record layout is the same as a
Hyperledger Fabric asset, so Fabric chaincode can replace this storage later.
"""
import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parents[2] / "data" / "audit_log.jsonl"
GENESIS = "0" * 64
_lock = threading.Lock()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def _record_hash(rec: dict) -> str:
    body = {k: v for k, v in rec.items() if k != "hash"}
    canon = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return sha256_text(canon)


def read_all(path: Path = None):
    path = path or LOG_PATH
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def append_record(user, action, input_sha256, tags, code_sha256,
                  path: Path = None):
    path = path or LOG_PATH
    with _lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        records = read_all(path)
        prev = records[-1]["hash"] if records else GENESIS
        rec = {
            "index": len(records),
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "user": user,
            "action": action,
            "input_sha256": input_sha256,
            "tags": sorted(tags),
            "code_sha256": code_sha256,
            "prev_hash": prev,
        }
        rec["hash"] = _record_hash(rec)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
        return rec


def verify_chain(path: Path = None):
    records = read_all(path)
    prev = GENESIS
    for i, rec in enumerate(records):
        if rec.get("index") != i:
            return {"valid": False, "records": len(records), "broken_at": i,
                    "reason": "index mismatch (record removed or reordered)"}
        if rec.get("prev_hash") != prev:
            return {"valid": False, "records": len(records), "broken_at": i,
                    "reason": "prev_hash does not match previous record"}
        if _record_hash(rec) != rec.get("hash"):
            return {"valid": False, "records": len(records), "broken_at": i,
                    "reason": "record content was changed"}
        prev = rec["hash"]
    return {"valid": True, "records": len(records), "broken_at": None,
            "reason": None, "head": prev}
