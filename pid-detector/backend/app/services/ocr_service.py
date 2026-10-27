import os
import re
import shutil

import cv2
import numpy as np
import pytesseract

_DEFAULT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if not shutil.which("tesseract") and os.path.exists(_DEFAULT_PATH):
    pytesseract.pytesseract.tesseract_cmd = _DEFAULT_PATH

# Accepts PT, LT, FCV, V-2, P-14, D-108, FIC-101
TAG_OK = re.compile(r"^[A-Z]{1,4}(-?\d{1,4}[A-Z]?)?$")
CONFIG = ("--oem 3 --psm 11 "
          "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")

TARGET_WIDTH = 3000   # small drawings are enlarged to about this width
MAX_SCALE = 4.0


_DIGIT_FIX = str.maketrans({"O": "0", "I": "1", "L": "1", "S": "5", "B": "8", "Z": "2"})
_SPLIT = re.compile(r"^([A-Z]{1,4}?)(-?)([0-9OILSBZ]{1,4})([A-Z]?)$")


def normalize_tag(text):
    """Fix O/0 and I/1 style misreads in the loop-number part of a tag.
    Letter-only tags (PT, LT, FCV) are left unchanged."""
    if re.search(r"\d", text) is None and "-" not in text:
        return text
    m = _SPLIT.match(text)
    if not m:
        return text
    prefix, dash, num, suffix = m.groups()
    if not any(c.isdigit() for c in num):
        return text  # no real digit, probably a letter word
    return prefix + dash + num.translate(_DIGIT_FIX) + suffix


def _to_bgr(img):
    arr = np.array(img)
    if arr.ndim == 2:
        return cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
    return arr[:, :, :3]


LETTERS_OK = re.compile(r"^[A-Z]{2,4}$")
NUMBER_OK = re.compile(r"^\d{1,4}[A-Z]?$")


def _strip_graphics(bw, sym):
    """Remove the bubble outline, process lines and big shapes so only
    text-sized marks remain. Tesseract fails when the text touches them."""
    inv = 255 - bw
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, connectivity=8)
    keep = np.zeros(n, dtype=bool)
    for i in range(1, n):
        w, h = st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]
        if w <= 0.45 * sym and h <= 0.45 * sym:
            keep[i] = True
    out = np.full_like(bw, 255)
    out[keep[lab]] = 0
    return out


def _words(bw):
    data = pytesseract.image_to_data(
        bw, config=CONFIG, output_type=pytesseract.Output.DICT)
    out = []
    for i, text in enumerate(data["text"]):
        text = text.strip().upper()
        try:
            conf = float(data["conf"][i])
        except ValueError:
            continue
        if text and conf >= 30:
            out.append({"t": text, "c": conf, "x": data["left"][i],
                        "y": data["top"][i], "w": data["width"][i],
                        "h": data["height"][i]})
    return out


def _best_word(bw):
    """Return (tag, conf). Two-line bubbles (letters over number) are joined
    as LETTERS-NUMBER. A tag with digits beats a letter-only tag."""
    words = _words(bw)
    cands = []  # (has_digit, conf, tag)
    for w in words:
        if TAG_OK.match(w["t"]) and not re.match(r"^[A-Z]\d", w["t"]):
            tag = normalize_tag(w["t"])
            cands.append((any(c.isdigit() for c in tag), w["c"], tag))
    for a in words:
        if not LETTERS_OK.match(a["t"]):
            continue
        for b in words:
            if not NUMBER_OK.match(b["t"]):
                continue
            gap = b["y"] - (a["y"] + a["h"])
            if gap < -0.3 * a["h"] or gap > 1.5 * a["h"]:
                continue
            if abs((a["x"] + a["w"] / 2) - (b["x"] + b["w"] / 2)) > max(a["w"], b["w"]):
                continue
            cands.append((True, min(a["c"], b["c"]), a["t"] + "-" + b["t"]))
    if not cands:
        return None
    best = max(cands, key=lambda c: (c[0], c[1]))
    return best[2], best[1]


def _read_crop(big, box, scale):
    h, w = big.shape[:2]
    x1, y1, x2, y2 = [v * scale for v in box]
    sym = max(x2 - x1, y2 - y1)
    m = sym * 0.8 + 10
    cx1, cy1 = int(max(0, x1 - m)), int(max(0, y1 - m))
    cx2, cy2 = int(min(w, x2 + m)), int(min(h, y2 + m))
    crop = big[cy1:cy2, cx1:cx2]
    if crop.size == 0:
        return None
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    clean = _strip_graphics(bw, sym)
    best = None
    for img in (clean, bw):  # cleaned first, raw as a fallback
        img = cv2.copyMakeBorder(img, 10, 10, 10, 10,
                                 cv2.BORDER_CONSTANT, value=255)
        best = _best_word(img)
        if best is None:  # vertical text
            best = _best_word(cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE))
        if best:
            break
    return best


BUBBLE_CLASSES = {f"class_{n}" for n in range(25, 31)}

# Common ISA-5.1 codes. A misread code within one edit of exactly one of
# these is snapped to it (FOI -> FQI, LAM -> LAH). Others are kept as read.
KNOWN_CODES = [
    "FIC", "FQ", "FQI", "FY", "FT", "FE", "FR", "FS", "FAL", "FAH", "FCV", "FV",
    "FI", "FRC", "FFIC", "LAL", "LAH", "LS", "LT", "LY", "LR", "LIC", "LCV", "LI",
    "LC", "LG", "LSH", "LSL", "PT", "PI", "PIC", "PCV", "PY", "PR", "PS", "PAL",
    "PAH", "PSV", "PSH", "PSL", "TT", "TI", "TIC", "TCV", "TY", "TR", "TS",
    "TAL", "TAH", "AT", "AIC", "AI", "AR", "AY", "HV", "HS", "HC", "ZT", "ZS",
    "ZSO", "ZSC", "XV", "SV", "WT", "WI", "WIC", "JT", "JI",
    "PDT", "PDI", "PDIC", "PDAH", "PDAL", "PDS", "PDY", "PDCV", "TIR", "TIRC",
    "TJ", "TE", "PE", "PG", "TW", "FG", "FO", "FQT", "FQY", "FQR", "FQIC", "FF", "FFC",
    "LV", "TV", "PV", "AE", "ST", "SC", "SI", "SIC", "SR", "VT", "VI",
]


def _edit1(a, b):
    """True if a and b differ by at most one substitution/insert/delete."""
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    short, long_ = (a, b) if len(a) < len(b) else (b, a)
    return any(long_[:i] + long_[i + 1:] == short for i in range(len(long_)))


def snap_code(letters):
    if letters in KNOWN_CODES:
        return letters
    near = [k for k in KNOWN_CODES if _edit1(letters, k)]
    same = [k for k in near if len(k) == len(letters)]  # a wrong letter is likelier than a lost one
    pick = same or near
    return pick[0] if len(pick) == 1 else letters


def _ocr_line(img, whitelist):
    cfg = f"--oem 3 --psm 7 -c tessedit_char_whitelist={whitelist}"
    data = pytesseract.image_to_data(
        img, config=cfg, output_type=pytesseract.Output.DICT)
    text, confs = "", []
    for t, c in zip(data["text"], data["conf"]):
        t = t.strip()
        try:
            c = float(c)
        except ValueError:
            continue
        if t and c >= 0:
            text += t
            confs.append(c)
    return text, (min(confs) if confs else 0.0)


def _vote(items):
    """(most common item, share of votes). Ties go to the longer item."""
    items = [i for i in items if i]
    if not items:
        return None, 0.0
    best = max(set(items), key=lambda i: (items.count(i), len(i)))
    return best, items.count(best) / len(items)


def _fix_digits(t):
    return t.translate(str.maketrans({"O": "0", "I": "1", "L": "1", "S": "5",
                                      "B": "8", "Z": "2", "Q": "0", "G": "6"}))


def _read_bubble(arr, box):
    """Instrument bubbles hold letters over a divider line over a number.
    The drawing text is only a few pixels tall, so several reads are taken
    (line by line, and whole bubble) and the most common answer wins."""
    x1, y1, x2, y2 = box
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    r = max(x2 - x1, y2 - y1) / 2
    half = int(r * 1.25) + 1
    H, W = arr.shape[:2]
    crop = arr[max(0, int(cy) - half):min(H, int(cy) + half),
               max(0, int(cx) - half):min(W, int(cx) + half)]
    if crop.size == 0 or min(crop.shape[:2]) < 6:
        return None

    letters_votes, digit_votes, confs = [], [], []
    for size in (240, 400):
        k = size / max(crop.shape[:2])
        big = cv2.resize(crop, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
        bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        h, w = bw.shape
        mask = np.zeros_like(bw)
        cv2.circle(mask, (w // 2, h // 2), int(r * k * 0.88), 255, -1)
        inner = np.where(mask > 0, bw, 255).astype(np.uint8)
        pad = lambda im: cv2.copyMakeBorder(im, 25, 25, 25, 25,
                                            cv2.BORDER_CONSTANT, value=255)

        # whole-bubble reads: letters line and number line come out as words
        for psm in (6, 11):
            cfg = (f"--oem 3 --psm {psm} -c tessedit_char_whitelist="
                   "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            words = pytesseract.image_to_string(pad(inner), config=cfg).split()
            for wd in words:
                if re.fullmatch(r"[A-Z]{2,4}", wd):
                    letters_votes.append(wd)
                elif re.fullmatch(r"[0-9OILSBZ]{2,3}", wd) and \
                        sum(c.isdigit() for c in wd) >= 1:
                    digit_votes.append(_fix_digits(wd))

        # line-by-line reads split at the divider
        dark = (inner < 128).sum(axis=1)
        lo, hi = int(h * 0.35), int(h * 0.65)
        row = lo + int(np.argmax(dark[lo:hi]))
        if dark[row] > 0.45 * (2 * r * k * 0.88):
            lt, lc = _ocr_line(pad(inner[:max(1, row - 3), :]),
                               "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            dt, dc = _ocr_line(pad(inner[row + 4:, :]), "0123456789")
            if re.fullmatch(r"[A-Z]{1,4}", lt.upper()):
                letters_votes.append(lt.upper())
                confs.append(lc)
            if re.fullmatch(r"\d{1,3}", dt):
                digit_votes.append(dt)
                confs.append(dc)

    letters, lshare = _vote([snap_code(v) for v in letters_votes])
    digits, dshare = _vote(digit_votes)
    if not letters:
        return None
    if digits and len(digits) == 1:
        digits = "0" + digits  # loop numbers on these sheets are two digits
    conf = round(100 * lshare * (dshare if digits else 1.0), 1)
    return (letters + "-" + digits if digits else letters), conf


def read_tags(img, detections):
    arr = _to_bgr(img)
    h, w = arr.shape[:2]
    scale = min(MAX_SCALE, max(1.0, TARGET_WIDTH / w))
    big = cv2.resize(arr, None, fx=scale, fy=scale,
                     interpolation=cv2.INTER_CUBIC) if scale > 1.0 else arr

    for det in detections:
        try:
            if det.get("class") in BUBBLE_CLASSES:
                res = _read_bubble(arr, det["bbox"]) or _read_crop(big, det["bbox"], scale)
            else:
                res = _read_crop(big, det["bbox"], scale)
        except Exception as e:
            print(f"OCR skipped: {e}")
            return detections
        if res and not any(c.isdigit() for c in res[0]):
            # letters-only reads are kept only for bubbles with a real ISA code
            if det.get("class") not in BUBBLE_CLASSES or res[0] not in KNOWN_CODES:
                res = None
        if res:
            det["tag"] = res[0]
            det["tag_confidence"] = round(res[1] / 100, 2)
    return detections
