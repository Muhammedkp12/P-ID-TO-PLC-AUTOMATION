from fastapi import APIRouter, HTTPException

from app.services.audit_service import GENESIS, _record_hash, read_all

router = APIRouter(prefix="/audit-block", tags=["audit"])


@router.get("/{index}")
def get_block(index: int):
    records = read_all()
    if index < 0 or index >= len(records):
        raise HTTPException(404, "Block not found.")
    rec = records[index]
    prev_hash = records[index - 1]["hash"] if index > 0 else GENESIS
    return {
        "record": rec,
        "content_valid": _record_hash(rec) == rec.get("hash"),
        "link_valid": rec.get("prev_hash") == prev_hash,
        "total": len(records),
        "prev_index": index - 1 if index > 0 else None,
        "next_index": index + 1 if index < len(records) - 1 else None,
    }