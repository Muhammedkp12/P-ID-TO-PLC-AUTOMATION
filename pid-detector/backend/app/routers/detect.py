import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.schemas.detection import DetectionResponse, HealthResponse, TrainRequest, TrainResponse
from app.services import yolo_service
from app.services.class_names import class_label
from app.services.postprocess import merge_symbol_and_tag_results
from app.utils.image_utils import decode_image

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/tiff", "image/webp"}


@router.post("/detect", response_model=DetectionResponse)
async def detect(file: UploadFile):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Upload a JPEG, PNG, TIFF, or WEBP scan.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        img = decode_image(image_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        raw_detections = yolo_service.detect_symbols_in_array(img)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    detections = merge_symbol_and_tag_results(img, raw_detections)
    for d in detections:
        d["class"] = f"{class_label(d['class'])} [{d['class']}]"

    height, width = img.shape[:2]

    return DetectionResponse(
        filename=file.filename or "upload",
        width=width,
        height=height,
        count=len(detections),
        detections=detections,
    )


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", model_loaded=yolo_service.is_model_loaded())


@router.post("/train", response_model=TrainResponse)
def train(req: TrainRequest):
    """
    Kicks off training/train.py as a background subprocess. Intended for
    internal/dev use (retraining on an updated symbol dataset), not for
    end users, so this endpoint should be protected or removed in a
    production deployment.
    """
    train_script = Path(__file__).resolve().parents[2] / "training" / "train.py"
    if not train_script.exists():
        raise HTTPException(status_code=404, detail="training/train.py not found.")

    try:
        subprocess.Popen(
            [
                sys.executable,
                str(train_script),
                "--data", req.data_yaml,
                "--epochs", str(req.epochs),
                "--imgsz", str(req.imgsz),
                "--batch", str(req.batch),
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start training: {e}")

    return TrainResponse(
        status="started",
        message="Training started in the background. Check server logs / runs/ dir for progress.",
    )