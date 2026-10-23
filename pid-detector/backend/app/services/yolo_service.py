"""
Loads the trained YOLO weights once at import time (not per-request, which
would be far too slow) and exposes detect_symbols() for the router to call.
"""
import os
from typing import List, Dict

import numpy as np
from ultralytics import YOLO

from app.utils.image_utils import decode_image, tile_image

MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "app/models/best.pt")
CONF_THRESHOLD = float(os.getenv("YOLO_CONF_THRESHOLD", "0.4"))
TILE_SIZE = int(os.getenv("YOLO_TILE_SIZE", "1280"))
TILE_OVERLAP = float(os.getenv("YOLO_TILE_OVERLAP", "0.2"))

_model = None


def get_model() -> YOLO:
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"YOLO weights not found at '{MODEL_PATH}'. "
                "Train a model (see training/train.py) or place best.pt in app/models/."
            )
        _model = YOLO(MODEL_PATH)
    return _model


def is_model_loaded() -> bool:
    return _model is not None or os.path.exists(MODEL_PATH)


def detect_symbols_in_array(img: np.ndarray) -> List[Dict]:
    """
    Runs tiled YOLO inference over an already-decoded P&ID sheet and returns
    raw, per-tile detections translated into full-image pixel coordinates.
    Overlap de-duplication happens downstream in postprocess.merge_detections.
    """
    model = get_model()
    tiles = tile_image(img, tile_size=TILE_SIZE, overlap=TILE_OVERLAP)

    raw_detections: List[Dict] = []

    for tile, x_off, y_off in tiles:
        results = model(tile, conf=CONF_THRESHOLD, verbose=False)
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                raw_detections.append({
                    "class": model.names[int(box.cls[0])],
                    "confidence": float(box.conf[0]),
                    "bbox": [x1 + x_off, y1 + y_off, x2 + x_off, y2 + y_off],
                })

    return raw_detections


def detect_symbols(image_bytes: bytes) -> List[Dict]:
    """Convenience wrapper: decode bytes then detect. Used when OCR tagging isn't needed."""
    img = decode_image(image_bytes)
    return detect_symbols_in_array(img)
