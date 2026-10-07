import io

from annopipe import ConsensusResult, needs_review, write_csv


def _result(item_id, agreement=1.0, box_iou=None):
    return ConsensusResult(item_id, "car", agreement, 3, box_iou)


def test_write_csv():
    buf = io.StringIO()
    n = write_csv([_result("a", 2 / 3, 0.5), _result("b")], buf)
    assert n == 2
    assert buf.getvalue().splitlines() == [
        "item_id,label,agreement,n_labelers,box_iou",
        "a,car,0.667,3,0.500",
        "b,car,1.000,3,",
    ]


def test_needs_review():
    results = [
        _result("ok", 1.0, 0.9),
        _result("split_vote", 0.5, 0.9),
        _result("sloppy_boxes", 1.0, 0.2),
        _result("no_boxes", 1.0, None),
    ]
    assert needs_review(results) == ["split_vote", "sloppy_boxes"]
