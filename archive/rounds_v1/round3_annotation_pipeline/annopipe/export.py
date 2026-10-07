"""Exporting consensus results for the QA team."""

from __future__ import annotations

import csv
from typing import Iterable, TextIO

from .consensus import ConsensusResult

COLUMNS = ["item_id", "label", "agreement", "n_labelers", "box_iou"]


def write_csv(results: Iterable[ConsensusResult], fh: TextIO) -> int:
    """Write results as CSV. Floats are rounded to 3 places; missing IoU is blank."""
    writer = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    n = 0
    for r in results:
        writer.writerow(
            {
                "item_id": r.item_id,
                "label": r.label,
                "agreement": f"{r.agreement:.3f}",
                "n_labelers": r.n_labelers,
                "box_iou": "" if r.box_iou is None else f"{r.box_iou:.3f}",
            }
        )
        n += 1
    return n


def needs_review(
    results: Iterable[ConsensusResult],
    min_agreement: float = 0.66,
    min_box_iou: float = 0.5,
) -> list[str]:
    """Item ids whose label agreement or box agreement is too low."""
    flagged = []
    for r in results:
        low_label = r.agreement < min_agreement
        low_box = r.box_iou is not None and r.box_iou < min_box_iou
        if low_label or low_box:
            flagged.append(r.item_id)
    return flagged
