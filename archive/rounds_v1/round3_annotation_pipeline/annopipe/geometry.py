"""Bounding-box helpers.

Two box formats appear in this codebase:

* ``xywh``  -> (x_min, y_min, width, height)   -- what labelers submit
* ``xyxy``  -> (x_min, y_min, x_max, y_max)     -- what everything internal uses
"""

from __future__ import annotations

from itertools import combinations
from typing import Sequence

Box = tuple[float, float, float, float]


def xywh_to_xyxy(box: Sequence[float]) -> Box:
    x, y, w, h = box
    if w < 0 or h < 0:
        raise ValueError(f"negative width/height in {box!r}")
    return (float(x), float(y), float(x + w), float(y + h))


def xyxy_to_xywh(box: Sequence[float]) -> Box:
    x1, y1, x2, y2 = box
    return (float(x1), float(y1), float(x2 - x1), float(y2 - y1))


def area(box: Box) -> float:
    x1, y1, x2, y2 = box
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def iou(a: Box, b: Box) -> float:
    """Intersection-over-union of two ``xyxy`` boxes, in [0, 1]."""
    ix1 = max(a[0], b[0])
    iy1 = max(a[1], b[1])
    ix2 = min(a[2], b[2])
    iy2 = min(a[3], b[3])
    inter = (ix2 - ix1) * (iy2 - iy1)
    union = area(a) + area(b) - inter
    return inter / union if union > 0 else 0.0


def mean_pairwise_iou(boxes: Sequence[Box]) -> float | None:
    """Average IoU over every pair of boxes; None if fewer than two boxes."""
    pairs = list(combinations(boxes, 2))
    if not pairs:
        return None
    return sum(iou(a, b) for a, b in pairs) / len(pairs)
