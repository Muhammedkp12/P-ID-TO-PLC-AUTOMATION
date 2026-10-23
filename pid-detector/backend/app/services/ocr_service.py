import os
import re
import shutil

import cv2
import numpy as np
import pytesseract

_DEFAULT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if not shutil.which("tesseract") and os.path.exists(_DEFAULT_PATH):
    pytesseract.pytesseract.tesseract_cmd = _DEFAULT_PATH

# PT, LT, FCV, V-2, P-14, D-108, FIC-101
TAG_OK = re.compile(r"^[A-Z]{1,4}(-?\d{1,4}[A-Z]?)?$")
CONFIG = ("--oem 3 --psm 11 "
          "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")


def _to_bgr(img):
    arr = np.array(img)
    if arr.ndim == 2:
        return cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
    return arr[:, :, :3]


def _read_crop(img, box):
    h, w = img.shape[:2]
    x1, y1, x2, y2 = box
    m = max(x2 - x1, y2 - y1) * 0.8 + 6
    cx1, cy1 = int(max(0, x1 - m)), int(max(0, y1 - m))
    cx2, cy2 = int(min(w, x2 + m)), int(min(h, y2 + m))
    crop = img[cy1:cy2, cx1:cx2]
    if crop.size == 0:
        return None
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    scale = max(1.0, 160 / max(gray.shape))
    gray = cv2.resize(gray, None, fx=scale, fy=scale,
                      interpolation=cv2.INTER_CUBIC)
    bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    bw = cv2.copyMakeBorder(bw, 10, 10, 10, 10,
                            cv2.BORDER_CONSTANT, value=255)
    data = pytesseract.image_to_data(
        bw, config=CONFIG, output_type=pytesseract.Output.DICT)
    best = None
    for text, conf in zip(data["text"], data["conf"]):
        text = text.strip().upper()
        try:
            conf = float(conf)
        except ValueError:
            continue
        if text and conf >= 30 and TAG_OK.match(text):
            if best is None or conf > best[1]:
                best = (text, conf)
    return best


def read_tags(img, detections):
    arr = _to_bgr(img)
    for det in detections:
        try:
            res = _read_crop(arr, det["bbox"])
        except Exception as e:
            print(f"OCR skipped: {e}")
            return detections
        if res:
            det["tag"] = res[0]
            det["tag_confidence"] = round(res[1] / 100, 2)
    return detections