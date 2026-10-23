"""
ocr_service.py

Extracts instrument tag text (e.g. "27-MOV-021", "PT-101") from a P&ID image.
This is deliberately a separate stage from YOLO symbol detection (see yolo_service.py) —
text recognition and object detection are different sub-problems, and keeping them
as separate, independently testable functions is what let us debug and improve each
without touching the other.

Engine: Tesseract via pytesseract. Chosen over EasyOCR for this project because:
  - No model weights to download at runtime (EasyOCR pulls ~100MB+ on first use,
    which is a real problem on a locked-down or offline deployment machine).
  - Ships as a standard apt/brew/choco package — easy for a teammate to install
    without a Python-CUDA dependency chain.
  - Good enough accuracy on clean, machine-printed diagram text (P&ID tags are
    printed CAD text, not handwriting — Tesseract's sweet spot).

If tag recall turns out too low on real scanned diagrams (vs. clean CAD exports),
EasyOCR is the documented fallback — see the note at the bottom of this file.
"""

from typing import TypedDict
import pytesseract
from PIL import Image


class OcrRegion(TypedDict):
    text: str
    bbox: list[float]        # [x1, y1, x2, y2] in original image pixel coordinates
    confidence: float        # 0-100, Tesseract's own confidence score


def extract_text_regions(
    image: Image.Image,
    min_confidence: float = 40.0,
    min_text_length: int = 2,
) -> list[OcrRegion]:
    """
    Run OCR over the full image and return one region per line of text,
    above a confidence and length floor.

    Tesseract returns one token per *word* — a single tag like "FT-204" can
    come back as two tokens ("FT", "-204") if there's a rendering/kerning
    gap around the hyphen. Returning raw word tokens would silently break
    tag matching, so this groups tokens by Tesseract's own (block, paragraph,
    line) indices and merges everything on the same line into one region
    before returning it — this is what actually gets tested and used
    downstream, not the raw per-word output.

    Args:
        image: a PIL Image (already opened/decoded — same object your YOLO
            service receives, so both stages share one decode of the upload).
        min_confidence: Tesseract confidence (0-100) below which a *token* is
            dropped before line-grouping. 40 is a permissive default tuned for
            small, dense diagram text — raise it if you're seeing too much
            OCR noise (see the false-positive note at the bottom of this file).
        min_text_length: drops single-character tokens, which are almost
            always noise (a stray line fragment Tesseract misreads as a letter).

    Returns:
        List of OcrRegion dicts, one per recognized line of text.
    """
    raw = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    # Group surviving tokens by (block, paragraph, line), then further split
    # on large horizontal gaps — two unrelated tags can land on the same
    # Tesseract "line" index if they sit at the same height in different
    # columns of the diagram, so line_num alone isn't a safe merge key.
    line_groups: dict[tuple[int, int, int], list[int]] = {}
    n = len(raw["text"])
    for i in range(n):
        text = raw["text"][i].strip()
        conf = float(raw["conf"][i])
        if not text or len(text) < min_text_length or conf < min_confidence:
            continue
        key = (raw["block_num"][i], raw["par_num"][i], raw["line_num"][i])
        line_groups.setdefault(key, []).append(i)

    # Median character height sets the gap threshold — a gap wider than
    # ~2.5x the text height is treated as "different tag", not a kerning gap.
    heights = [raw["height"][i] for group in line_groups.values() for i in group]
    median_h = sorted(heights)[len(heights) // 2] if heights else 20
    max_gap = median_h * 2.5

    clusters: list[list[int]] = []
    for token_indices in line_groups.values():
        token_indices.sort(key=lambda i: raw["left"][i])
        current: list[int] = [token_indices[0]]
        for idx in token_indices[1:]:
            prev_idx = current[-1]
            gap = raw["left"][idx] - (raw["left"][prev_idx] + raw["width"][prev_idx])
            if gap > max_gap:
                clusters.append(current)
                current = [idx]
            else:
                current.append(idx)
        clusters.append(current)

    regions: list[OcrRegion] = []
    for token_indices in clusters:
        # Tokens come out in reading order already; join and take the union bbox.
        token_indices.sort(key=lambda i: raw["left"][i])
        text = "".join(raw["text"][i].strip() for i in token_indices) \
            if _looks_hyphen_joined(raw, token_indices) \
            else " ".join(raw["text"][i].strip() for i in token_indices)

        xs1 = [raw["left"][i] for i in token_indices]
        ys1 = [raw["top"][i] for i in token_indices]
        xs2 = [raw["left"][i] + raw["width"][i] for i in token_indices]
        ys2 = [raw["top"][i] + raw["height"][i] for i in token_indices]
        confs = [float(raw["conf"][i]) for i in token_indices]

        regions.append({
            "text": text,
            "bbox": [float(min(xs1)), float(min(ys1)), float(max(xs2)), float(max(ys2))],
            "confidence": round(sum(confs) / len(confs), 1),
        })

    return regions


def _looks_hyphen_joined(raw: dict, token_indices: list[int]) -> bool:
    """
    Heuristic: if any token on this line is bare punctuation ('-', '/', ':')
    or starts/ends with one, the line is a single tag like "FT-204" split by
    kerning, not separate words — join with no space. Otherwise join with a
    space (e.g. a real two-word label).
    """
    for i in token_indices:
        t = raw["text"][i].strip()
        if t and (t[0] in "-/:" or t[-1] in "-/:"):
            return True
    return False


# --- Fallback note ---
# If Tesseract's recall is too low on your actual test diagrams (common with
# scanned/photographed P&IDs rather than clean CAD exports), swap in EasyOCR:
#
#   import easyocr
#   reader = easyocr.Reader(['en'], gpu=False)
#   results = reader.readtext(image_path)  # returns [(bbox_poly, text, conf), ...]
#
# EasyOCR's bbox is a 4-point polygon, not [x1,y1,x2,y2] — convert with
# min/max over the polygon's x and y values before passing to
# postprocess.associate_tags_with_symbols().
