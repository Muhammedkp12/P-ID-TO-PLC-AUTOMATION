"""Finds instrument bubbles (circles with text) directly from the drawing.

The YOLO model misses many bubbles, especially on drawing styles it was not
trained on. Bubbles are plain circles, so a Hough circle search plus a
'is this really a closed ring' check finds them reliably on clean sheets.
"""
import cv2
import numpy as np

BUBBLE_CLASS = "class_25"


_ANGLES = np.linspace(0, 2 * np.pi, 96, endpoint=False)
_COS, _SIN = np.cos(_ANGLES), np.sin(_ANGLES)


def _ring_score(ink, cx, cy, r):
    """Share of points on the circle that sit on ink. `ink` is the dark map
    already thickened by one pixel."""
    h, w = ink.shape
    xs = np.rint(cx + r * _COS).astype(int)
    ys = np.rint(cy + r * _SIN).astype(int)
    ok = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)
    if ok.sum() < len(_ANGLES) * 0.8:
        return 0.0
    return float(ink[ys[ok], xs[ok]].mean())


def _refine(ink, cx, cy, r):
    """Hough centres are a few pixels off. Search nearby for the best ring."""
    best = (_ring_score(ink, cx, cy, r), cx, cy, r)
    for dx in range(-5, 6):
        for dy in range(-5, 6):
            for dr in range(-5, 6):
                sc = _ring_score(ink, cx + dx, cy + dy, r + dr)
                if sc > best[0]:
                    best = (sc, cx + dx, cy + dy, r + dr)
    return best


def detect_bubbles(img):
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    dark = (gray < 150).astype(np.uint8)
    ink = cv2.dilate(dark, np.ones((3, 3), np.uint8))

    min_r = max(8, int(w * 0.014))
    max_r = max(min_r + 4, int(w * 0.06))
    circles = cv2.HoughCircles(
        blur, cv2.HOUGH_GRADIENT, dp=1, minDist=min_r * 1.5,
        param1=50, param2=8, minRadius=min_r, maxRadius=max_r)
    if circles is None:
        return []

    cands = []
    for cx, cy, r in circles[0][:600]:
        score, cx, cy, r = _refine(ink, float(cx), float(cy), float(r))
        if score < 0.9:
            continue
        # a bubble holds text: some ink inside, but not a filled disc
        mask = np.zeros_like(dark)
        cv2.circle(mask, (int(cx), int(cy)), max(1, int(r * 0.8)), 1, -1)
        inside = dark[mask > 0].mean()
        if not 0.03 <= inside <= 0.5:
            continue
        cands.append((float(cx), float(cy), float(r), score))
    if not cands:
        return []

    # a loop of a digit or letter inside a bubble is not a bubble
    cands = [c for c in cands
             if not any(o is not c and o[2] > 1.5 * c[2] and
                        np.hypot(o[0] - c[0], o[1] - c[1]) < o[2] for o in cands)]

    # bubbles on one sheet share a size: keep the most common radius group
    radii = np.array([c[2] for c in cands])
    best_med, best_n = None, 0
    for r0 in radii:
        grp = radii[np.abs(radii - r0) <= 0.2 * r0]
        if len(grp) > best_n:
            best_n, best_med = len(grp), float(np.median(grp))
    cands = [c for c in cands if abs(c[2] - best_med) <= 0.25 * best_med]

    # drop duplicates (Hough often returns a ring twice)
    cands.sort(key=lambda c: -c[3])
    kept = []
    for c in cands:
        if all(np.hypot(c[0] - k[0], c[1] - k[1]) > 0.8 * c[2] for k in kept):
            kept.append(c)

    return [{"class": BUBBLE_CLASS, "confidence": round(s, 2),
             "bbox": [round(cx - r, 1), round(cy - r, 1),
                      round(cx + r, 1), round(cy + r, 1)]}
            for cx, cy, r, s in kept]
