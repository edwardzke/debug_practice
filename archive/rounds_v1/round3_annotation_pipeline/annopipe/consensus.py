"""Aggregating multiple labelers' annotations into a consensus per item."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from .geometry import mean_pairwise_iou
from .parse import Annotation


@dataclass(frozen=True)
class ConsensusResult:
    item_id: str
    label: str
    agreement: float          # fraction of labelers who chose ``label``
    n_labelers: int
    box_iou: float | None     # mean pairwise IoU of the submitted boxes


def latest_per_labeler(annotations: Iterable[Annotation]) -> list[Annotation]:
    """Keep only each labeler's most recent annotation (later lines win)."""
    by_labeler: dict[str, Annotation] = {}
    for ann in annotations:
        by_labeler[ann.labeler_id] = ann
    return list(by_labeler.values())


def majority_label(annotations: Iterable[Annotation]) -> str | None:
    """Most common label. Ties are broken alphabetically so results are stable."""
    counts = Counter(a.label for a in annotations)
    if not counts:
        return None
    return counts.most_common(1)[0][0]


def group_by_item(annotations: Iterable[Annotation]) -> dict[str, list[Annotation]]:
    groups: dict[str, list[Annotation]] = defaultdict(list)
    for ann in annotations:
        groups[ann.item_id].append(ann)
    return dict(groups)


def build_consensus(
    annotations: Iterable[Annotation], min_labelers: int = 2
) -> list[ConsensusResult]:
    """Consensus for every item labeled by at least ``min_labelers`` labelers.

    ``annotations`` may be any iterable, including a one-shot generator such
    as the one returned by ``parse.load_jsonl``. Results are sorted by item_id.
    """
    all_labelers = {a.labeler_id for a in annotations}
    if len(all_labelers) < min_labelers:
        return []

    results: list[ConsensusResult] = []
    for item_id, anns in group_by_item(annotations).items():
        anns = latest_per_labeler(anns)
        if len(anns) < min_labelers:
            continue
        label = majority_label(anns)
        assert label is not None
        votes = sum(1 for a in anns if a.label == label)
        boxes = [a.bbox for a in anns if a.bbox is not None]
        results.append(
            ConsensusResult(
                item_id=item_id,
                label=label,
                agreement=votes / len(anns),
                n_labelers=len(anns),
                box_iou=mean_pairwise_iou(boxes),
            )
        )
    results.sort(key=lambda r: r.item_id)
    return results
