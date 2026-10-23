"""
Two jobs:
1. Tiling (yolo_service) means the same real-world symbol can be detected
   more than once across overlapping tiles - dedupe with class-aware NMS.
2. Attach OCR tag text (ocr_service) to the surviving detections.
"""
from typing import Dict, List

import numpy as np

from app.services.ocr_service import read_tags


def _iou(box_a: List[float], box_b: List[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1, inter_y1 = max(ax1, bx1), max(ay1, by1)
    inter_x2, inter_y2 = min(ax2, bx2), min(ay2, by2)
    inter_w, inter_h = max(0.0, inter_x2 - inter_x1), max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - inter_area
    return inter_area / union if union > 0 else 0.0


def dedupe_detections(detections: List[Dict], iou_threshold: float = 0.5) -> List[Dict]:
    """Class-aware greedy NMS, keeping the highest-confidence box in each cluster."""
    by_class: Dict[str, List[Dict]] = {}
    for det in detections:
        by_class.setdefault(det["class"], []).append(det)

    kept: List[Dict] = []
    for class_dets in by_class.values():
        class_dets.sort(key=lambda d: d["confidence"], reverse=True)
        chosen: List[Dict] = []
        for det in class_dets:
            if all(_iou(det["bbox"], c["bbox"]) < iou_threshold for c in chosen):
                chosen.append(det)
        kept.extend(chosen)

    return kept


def merge_symbol_and_tag_results(
    img: np.ndarray,
    raw_detections: List[Dict],
    iou_threshold: float = 0.5,
) -> List[Dict]:
    """Full postprocess pipeline: dedupe tile overlaps, then OCR each survivor's tag."""
    deduped = dedupe_detections(raw_detections, iou_threshold=iou_threshold)
    deduped.sort(key=lambda d: d["confidence"], reverse=True)
    return read_tags(img, deduped)
