"""
P&ID sheets are usually huge (A1/A0 scanned drawings), far larger than the
image size YOLO was trained on. Downscaling the whole sheet in one shot
destroys small symbols and tag text, so we tile the image into overlapping
crops, run detection per-tile, then let postprocess.py merge everything
back into full-image coordinates.
"""
from typing import List, Tuple
import cv2
import numpy as np


def decode_image(image_bytes: bytes) -> np.ndarray:
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image. Is the file a valid image?")
    return img


def tile_image(
    img: np.ndarray,
    tile_size: int = 1280,
    overlap: float = 0.2,
) -> List[Tuple[np.ndarray, int, int]]:
    """
    Split img into overlapping tiles.
    Returns a list of (tile, x_offset, y_offset) so detections can later be
    translated back into full-image coordinates.
    """
    h, w = img.shape[:2]
    stride = int(tile_size * (1 - overlap))
    tiles = []

    if h <= tile_size and w <= tile_size:
        return [(img, 0, 0)]

    for y in range(0, h, stride):
        for x in range(0, w, stride):
            x_end = min(x + tile_size, w)
            y_end = min(y + tile_size, h)
            x_start = max(0, x_end - tile_size)
            y_start = max(0, y_end - tile_size)
            tile = img[y_start:y_end, x_start:x_end]
            tiles.append((tile, x_start, y_start))
            if x_end == w:
                break
        if y_end == h:
            break

    return tiles


def resize_max_dim(img: np.ndarray, max_dim: int = 1280) -> Tuple[np.ndarray, float]:
    """Resize so the longest side == max_dim, return the scale factor used."""
    h, w = img.shape[:2]
    scale = max_dim / max(h, w)
    if scale >= 1:
        return img, 1.0
    resized = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return resized, scale
