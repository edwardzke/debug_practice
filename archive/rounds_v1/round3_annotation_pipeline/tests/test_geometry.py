import pytest

from annopipe import iou, mean_pairwise_iou, xywh_to_xyxy, xyxy_to_xywh


def test_xywh_roundtrip():
    box = (5.0, 6.0, 7.0, 8.0)
    assert xywh_to_xyxy(box) == (5.0, 6.0, 12.0, 14.0)
    assert xyxy_to_xywh(xywh_to_xyxy(box)) == box


def test_negative_size_rejected():
    with pytest.raises(ValueError):
        xywh_to_xyxy((0, 0, -1, 5))


def test_iou_identical():
    assert iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0


def test_iou_partial_overlap():
    assert iou((0, 0, 10, 10), (5, 0, 15, 10)) == pytest.approx(50 / 150)


def test_iou_contained():
    assert iou((0, 0, 10, 10), (2, 2, 4, 4)) == pytest.approx(4 / 100)


def test_iou_disjoint_side_by_side():
    assert iou((0, 0, 10, 10), (20, 0, 30, 10)) == 0.0


def test_iou_disjoint_diagonal():
    assert iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0


def test_iou_degenerate():
    assert iou((0, 0, 0, 0), (0, 0, 0, 0)) == 0.0


def test_mean_pairwise_iou():
    boxes = [(0, 0, 10, 10), (0, 0, 10, 10), (20, 20, 30, 30)]
    assert mean_pairwise_iou(boxes) == pytest.approx(1 / 3)
    assert mean_pairwise_iou(boxes[:1]) is None
