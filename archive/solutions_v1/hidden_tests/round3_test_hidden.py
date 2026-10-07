"""Hidden test for the BRIEF.md bug report (streaming input yields empty report)."""
import json

from annopipe import build_consensus, iter_annotations


def test_build_consensus_accepts_generator():
    lines = [
        json.dumps({"item_id": "i", "labeler_id": 1, "label": "car"}),
        json.dumps({"item_id": "i", "labeler_id": 2, "label": "car"}),
    ]
    results = build_consensus(iter_annotations(lines))
    assert [r.item_id for r in results] == ["i"]
