"""
ocr_service.py

Reads the equipment / instrument tag (e.g. "27-MOV-021", "PT-101") for each
symbol that YOLO detected.

For every detection the bounding box is cropped (with padding, because tags
often sit beside a symbol rather than inside it), upscaled 2x, thresholded
with Otsu, and run through Tesseract. All tokens on a text line are merged
left-to-right, so multi-part tags are not truncated to a single token.

postprocess.py calls:  read_tags(img, detections) -> detections with "tag" set
"""
import logging
import os
import re
import shutil
from typing import Dict, List, Optional

import cv2
import numpy as np
import pytesseract

logger = logging.getLogger(__name__)

# Windows: fall back to the default install path if tesseract is not on PATH.
_DEFAULT_WIN_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if shutil.which("tesseract") is None and os.path.exists(_DEFAULT_WIN_TESSERACT):
    pytesseract.pytesseract.tesseract_cmd = _DEFAULT_WIN_TESSERACT

# A tag needs at least one letter and one digit, made of 1-4 hyphen-separated
# parts, e.g. 27-MOV-021, PT-101, FV310.
TAG_PATTERN = re.compile(
    r"^(?=.*[A-Z])(?=.*\d)[A-Z0-9]{1,6}(?:-[A-Z0-9]{1,6}){0,3}$"
)

MIN_TOKEN_CONF = 40.0   # Tesseract confidence (0-100) below which a token is dropped
PAD_RATIO = 0.5         # how far to grow each box (fraction of its larger side)
MIN_PAD_PX = 12
UPSCALE = 2
TESSERACT_CONFIG = "--oem 3 --psm 11"  # sparse text: finds scattered labels


def _to_gray(crop: np.ndarray) -> np.ndarray:
    if crop.ndim == 2:
        return crop
    if crop.shape[2] == 4:
        return cv2.cvtColor(crop, cv2.COLOR_BGRA2GRAY)
    return cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)


def _preprocess(crop: np.ndarray) -> np.ndarray:
    gray = _to_gray(crop)
    gray = cv2.resize(gray, None, fx=UPSCALE, fy=UPSCALE, interpolation=cv2.INTER_CUBIC)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # white border helps Tesseract with text that touches the crop edge
    return cv2.copyMakeBorder(binary, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)


def _clean(token: str) -> str:
    t = token.strip().upper()
    t = re.sub("[\u2010-\u2015\u2212_]", "-", t)  # dash look-alikes -> '-'
    return re.sub(r"[^A-Z0-9-]", "", t)


def _group_lines(tokens: List[Dict]) -> List[List[Dict]]:
    """Group tokens whose vertical centres are close into text lines."""
    tokens = sorted(tokens, key=lambda t: t["top"] + t["h"] / 2)
    lines: List[List[Dict]] = []
    for tok in tokens:
        cy = tok["top"] + tok["h"] / 2
        if lines:
            line = lines[-1]
            line_cy = sum(t["top"] + t["h"] / 2 for t in line) / len(line)
            line_h = max(t["h"] for t in line)
            if abs(cy - line_cy) <= 0.6 * max(line_h, tok["h"]):
                line.append(tok)
                continue
        lines.append([tok])
    return lines


def _join(tokens: List[Dict]) -> str:
    """Merge tokens left-to-right into one string, hyphen-joined."""
    text = ""
    for tok in sorted(tokens, key=lambda t: t["left"]):
        part = tok["text"]
        if not text:
            text = part
        elif text.endswith("-") or part.startswith("-"):
            text += part
        else:
            text += "-" + part
    return re.sub(r"-{2,}", "-", text).strip("-")


def _mean_conf(tokens: List[Dict]) -> float:
    return sum(t["conf"] for t in tokens) / len(tokens)


def _read_tag_for_box(img: np.ndarray, bbox: List[float]) -> Optional[str]:
    h_img, w_img = img.shape[:2]
    x1, y1, x2, y2 = bbox
    pad = max(int(max(x2 - x1, y2 - y1) * PAD_RATIO), MIN_PAD_PX)
    cx1, cy1 = max(0, int(x1 - pad)), max(0, int(y1 - pad))
    cx2, cy2 = min(w_img, int(x2 + pad)), min(h_img, int(y2 + pad))

    crop = img[cy1:cy2, cx1:cx2]
    if crop.size == 0 or crop.shape[0] < 8 or crop.shape[1] < 8:
        return None

    data = pytesseract.image_to_data(
        _preprocess(crop), config=TESSERACT_CONFIG, output_type=pytesseract.Output.DICT
    )

    tokens: List[Dict] = []
    for i, raw_text in enumerate(data["text"]):
        text = _clean(raw_text)
        try:
            conf = float(data["conf"][i])
        except (TypeError, ValueError):
            continue
        if not text or conf < MIN_TOKEN_CONF:
            continue
        tokens.append(
            {
                "text": text,
                "left": data["left"][i],
                "top": data["top"][i],
                "h": data["height"][i],
                "conf": conf,
            }
        )
    if not tokens:
        return None

    # Candidates: each text line merged, each single token, and everything in
    # the crop merged (instrument bubbles put "PT" and "101" on two lines).
    lines = _group_lines(tokens)
    candidates = [(_join(line), _mean_conf(line)) for line in lines]
    candidates += [(t["text"], t["conf"]) for t in tokens]
    ordered = [t for line in lines for t in sorted(line, key=lambda t: t["left"])]
    candidates.append((_join(ordered), _mean_conf(ordered)))

    best: Optional[tuple] = None
    for text, conf in candidates:
        if len(text) < 3 or not TAG_PATTERN.match(text):
            continue
        if best is None or (conf, len(text)) > (best[1], len(best[0])):
            best = (text, conf)
    return best[0] if best else None


def read_tags(img: np.ndarray, detections: List[Dict]) -> List[Dict]:
    """Return a copy of each detection with its OCR'd "tag" (or None)."""
    results: List[Dict] = []
    ocr_available = True
    for det in detections:
        out = dict(det)
        out["tag"] = None
        if ocr_available:
            try:
                out["tag"] = _read_tag_for_box(img, det["bbox"])
            except pytesseract.TesseractNotFoundError:
                logger.warning(
                    "Tesseract is not installed or not on PATH - tags will be empty."
                )
                ocr_available = False
        results.append(out)
    return results