"""Parsing labeler submissions from JSON Lines.

Each line looks like::

    {"item_id": "img_001", "labeler_id": 42, "label": "car",
     "bbox": [10, 20, 30, 40], "attributes": {"occluded": true}}

``bbox`` (optional) is in **xywh** format. ``labeler_id`` may arrive as an int
or a string depending on which upstream tool produced the file; it is always
normalized to ``str``. ``attributes`` is optional.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

from .geometry import Box, xywh_to_xyxy, xyxy_to_xywh

DEFAULT_RECORD: dict[str, Any] = {
    "bbox": None,
    "attributes": {},
}


class ParseError(ValueError):
    def __init__(self, lineno: int, message: str) -> None:
        super().__init__(f"line {lineno}: {message}")
        self.lineno = lineno


@dataclass(frozen=True)
class Annotation:
    item_id: str
    labeler_id: str
    label: str
    bbox: Box | None = None  # xyxy
    attributes: dict[str, Any] = field(default_factory=dict, compare=False, hash=False)


def parse_record(raw: dict[str, Any]) -> Annotation:
    record = dict(DEFAULT_RECORD)
    record["attributes"].update(raw.get("attributes") or {})
    for key in ("item_id", "labeler_id", "label"):
        if key not in raw:
            raise KeyError(key)
        record[key] = raw[key]
    if raw.get("bbox") is not None:
        record["bbox"] = xyxy_to_xywh(raw["bbox"])
    return Annotation(
        item_id=str(record["item_id"]),
        labeler_id=record["labeler_id"],
        label=str(record["label"]).strip().lower(),
        bbox=record["bbox"],
        attributes=record["attributes"],
    )


def iter_annotations(lines: Iterable[str]) -> Iterator[Annotation]:
    """Yield annotations, skipping blank lines and ``#`` comments."""
    for lineno, line in enumerate(lines, start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ParseError(lineno, f"invalid JSON ({exc.msg})") from None
        try:
            yield parse_record(raw)
        except KeyError as exc:
            raise ParseError(lineno, f"missing field {exc.args[0]!r}") from None
        except (TypeError, ValueError) as exc:
            raise ParseError(lineno, str(exc)) from None


def load_jsonl(path: str | Path) -> Iterator[Annotation]:
    with open(path, encoding="utf-8") as fh:
        yield from iter_annotations(fh)
