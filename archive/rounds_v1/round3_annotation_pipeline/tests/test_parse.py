import pytest

from annopipe import ParseError, iter_annotations
from conftest import line


def test_parses_and_skips_comments(sample_lines):
    anns = list(iter_annotations(sample_lines))
    assert len(anns) == 6
    assert anns[0].item_id == "img_1"


def test_labels_are_normalized(sample_lines):
    anns = list(iter_annotations(sample_lines))
    assert {a.label for a in anns if a.item_id == "img_2"} == {"pedestrian"}


def test_bbox_converted_to_xyxy():
    (a,) = iter_annotations([line(item_id="i", labeler_id=1, label="car", bbox=[10, 20, 30, 40])])
    assert a.bbox == (10.0, 20.0, 40.0, 60.0)


def test_missing_bbox_is_none():
    (a,) = iter_annotations([line(item_id="i", labeler_id=1, label="car")])
    assert a.bbox is None


def test_labeler_id_normalized_to_str():
    anns = list(
        iter_annotations(
            [
                line(item_id="i", labeler_id=7, label="car"),
                line(item_id="i", labeler_id="7", label="car"),
            ]
        )
    )
    assert anns[0].labeler_id == anns[1].labeler_id == "7"


def test_attributes_do_not_leak_between_records():
    a, b = iter_annotations(
        [
            line(item_id="i", labeler_id=1, label="car", attributes={"occluded": True}),
            line(item_id="i", labeler_id=2, label="car"),
        ]
    )
    assert a.attributes == {"occluded": True}
    assert b.attributes == {}


def test_bad_json_reports_line_number():
    with pytest.raises(ParseError) as exc_info:
        list(iter_annotations([line(item_id="i", labeler_id=1, label="x"), "{oops"]))
    assert exc_info.value.lineno == 2


def test_missing_field_reports_line_number():
    with pytest.raises(ParseError, match="label"):
        list(iter_annotations([line(item_id="i", labeler_id=1)]))
