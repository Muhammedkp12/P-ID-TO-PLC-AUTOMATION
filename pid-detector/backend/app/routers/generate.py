from fastapi import APIRouter, Form, HTTPException, UploadFile

from app.routers.detect import ALLOWED_CONTENT_TYPES
from app.services import audit_service, yolo_service
from app.services.class_names import class_label
from app.services.codegen_service import generate_st
from app.services.postprocess import merge_symbol_and_tag_results
from app.services.verify_service import verify_st
from app.utils.image_utils import decode_image

router = APIRouter()


@router.post("/generate")
async def generate(file: UploadFile, user: str = Form("anonymous")):
    """Image in; detections, tags, Structured Text, verify result and audit hash out."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(400, f"Unsupported file type '{file.content_type}'.")
    data = await file.read()
    if not data:
        raise HTTPException(400, "Uploaded file is empty.")
    try:
        img = decode_image(data)
    except ValueError as e:
        raise HTTPException(400, str(e))
    try:
        raw = yolo_service.detect_symbols_in_array(img)
    except FileNotFoundError as e:
        raise HTTPException(503, str(e))

    detections = merge_symbol_and_tag_results(img, raw)
    for d in detections:
        d["class"] = f"{class_label(d['class'])} [{d['class']}]"

    code, warnings = generate_st(detections)
    warnings = [w for w in warnings if "has no tag" not in w]
    verify = verify_st(code)
    tags = [d["tag"] for d in detections if d.get("tag")]

    rec = audit_service.append_record(
        user=user, action="generate_plc",
        input_sha256=audit_service.sha256_bytes(data),
        tags=tags, code_sha256=audit_service.sha256_text(code))

    h, w = img.shape[:2]
    return {
        "filename": file.filename or "upload",
        "width": w, "height": h,
        "count": len(detections),
        "tagged": len(tags),
        "detections": detections,
        "code": code,
        "warnings": warnings,
        "verify": verify,
        "audit": {"index": rec["index"], "hash": rec["hash"],
                  "timestamp": rec["timestamp"]},
    }
