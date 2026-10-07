import pytest

from annopipe import build_consensus, iter_annotations, majority_label
from conftest import ann, line


def test_majority_label_simple():
    anns = [ann("i", 1, "car"), ann("i", 2, "car"), ann("i", 3, "bus")]
    assert majority_label(anns) == "car"


def test_majority_label_empty():
    assert majority_label([]) is None


def test_majority_tie_broken_alphabetically():
    anns = [ann("i", 1, "dog"), ann("i", 2, "cat")]
    assert majority_label(anns) == "cat"
    assert majority_label(list(reversed(anns))) == "cat"


def test_build_consensus_end_to_end(sample_lines):
    results = build_consensus(list(iter_annotations(sample_lines)))
    assert [r.item_id for r in results] == ["img_1", "img_2"]  # img_3 has 1 labeler
    img1, img2 = results
    assert img1.label == "car"
    assert img1.n_labelers == 3
    assert img1.agreement == pytest.approx(2 / 3)
    assert img2.label == "pedestrian"
    assert img2.agreement == 1.0
    assert img2.box_iou is None


def test_box_iou_uses_converted_boxes(sample_lines):
    img1 = build_consensus(list(iter_annotations(sample_lines)))[0]
    # xywh [0,0,10,10] vs [1,1,10,10] -> xyxy (0,0,10,10) vs (1,1,11,11): IoU 81/119
    expected = (81 / 119 + 1.0 + 81 / 119) / 3
    assert img1.box_iou == pytest.approx(expected)


def test_latest_annotation_per_labeler_wins():
    lines = [
        line(item_id="i", labeler_id=7, label="cat"),
        line(item_id="i", labeler_id="7", label="dog"),
        line(item_id="i", labeler_id="8", label="dog"),
    ]
    (r,) = build_consensus(list(iter_annotations(lines)))
    assert r.n_labelers == 2
    assert r.label == "dog"
    assert r.agreement == 1.0


def test_min_labelers_filter():
    anns = [ann("a", 1, "x"), ann("a", 2, "x"), ann("b", 1, "y")]
    assert [r.item_id for r in build_consensus(anns, min_labelers=1)] == ["a", "b"]
    assert [r.item_id for r in build_consensus(anns, min_labelers=3)] == []


def test_empty_input():
    assert build_consensus([]) == []
