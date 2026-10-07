import json

import pytest

from annopipe import Annotation


def line(**fields) -> str:
    return json.dumps(fields)


def ann(item_id, labeler_id, label, bbox=None) -> Annotation:
    """Build an Annotation directly (bbox already in xyxy)."""
    return Annotation(item_id=item_id, labeler_id=str(labeler_id), label=label, bbox=bbox)


@pytest.fixture
def sample_lines():
    return [
        "# exported 2026-10-01",
        line(item_id="img_1", labeler_id=1, label="car", bbox=[0, 0, 10, 10]),
        line(item_id="img_1", labeler_id=2, label="car", bbox=[1, 1, 10, 10]),
        line(item_id="img_1", labeler_id=3, label="truck", bbox=[0, 0, 10, 10]),
        "",
        line(item_id="img_2", labeler_id=1, label="Pedestrian"),
        line(item_id="img_2", labeler_id=2, label="pedestrian"),
        line(item_id="img_3", labeler_id=1, label="cyclist"),
    ]
