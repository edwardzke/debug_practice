# Round 3 Solutions — Annotation Consensus Pipeline (SPOILERS)

6 bugs: 5 caught by tests, 1 only in the bug report. Reference fix: `round3.patch`.
`export.py` is bug-free.

---

## Bug 1 — IoU without clamping (`geometry.py`, `iou`)
**Symptom:** `test_iou_disjoint_side_by_side` gives -0.333 and `test_iou_disjoint_diagonal` gives 1.0 (!),
so `test_mean_pairwise_iou` fails too.
- **Hint 1:** For boxes that don't overlap, what is the sign of `ix2 - ix1`? What happens when both differences are negative?
- **Fix:** `inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)`.
- **Why:** Two negative widths multiply to a positive "intersection". This is the most common IoU bug, and it's very on-theme for Scale.

## Bug 2 — Wrong box conversion direction (`parse.py`, `parse_record`)
**Symptom:** `test_bbox_converted_to_xyxy`: `[10,20,30,40]` becomes `(10,20,20,20)`, so `test_box_iou_uses_converted_boxes` fails as well.
- **Hint 1:** The module docstring says input boxes are **xywh**. Internally everything is **xyxy**.
- **Hint 2:** Read the function name being called, letter by letter.
- **Fix:** `xywh_to_xyxy(raw["bbox"])`. The buggy import line also pulled in `xyxy_to_xywh`.

## Bug 3 — Shallow copy of a nested default (`parse.py`, `parse_record`)
**Symptom:** `test_attributes_do_not_leak_between_records`: the second record inherits `{"occluded": True}`.
- **Hint 1:** `dict(DEFAULT_RECORD)` copies the outer dict. What about `record["attributes"]`?
- **Fix:** `copy.deepcopy(DEFAULT_RECORD)`, or build the dict fresh each call (`{"bbox": None, "attributes": {}}`).
- **Why:** `.update()` mutates the module-level default, so every later record carries the old attributes.

## Bug 4 — `labeler_id` not normalized (`parse.py`, `parse_record`)
**Symptom:** `test_labeler_id_normalized_to_str`, `test_latest_annotation_per_labeler_wins`: labeler `7` and `"7"` count as two people.
- **Hint 1:** The docstring promises `labeler_id` is always a `str`. Check the dataclass field type against what is actually passed in.
- **Fix:** `labeler_id=str(record["labeler_id"])`.
- **Why:** `{7: ..., "7": ...}` has two keys, so per-labeler dedup silently fails and agreement drops from 1.0 to 0.667.

## Bug 5 — Tie-break depends on input order (`consensus.py`, `majority_label`)
**Symptom:** `test_majority_tie_broken_alphabetically`: `["dog","cat"]` gives `"dog"`.
- **Hint 1:** What does `Counter.most_common` do with ties? (It keeps first-seen order.)
- **Fix:** `best = max(counts.values()); return min(l for l, n in counts.items() if n == best)`.
- **Why:** Results that depend on file order aren't reproducible, and that's bad for a data pipeline.

## Bug 6 (bug report DATA-1450) — Generator consumed twice (`consensus.py`, `build_consensus`)
**Symptom:** `load_jsonl()` returns a generator. `all_labelers = {...for a in annotations}` exhausts it, so
`group_by_item(annotations)` sees nothing and the CSV is empty. With list input (all the tests use lists) it works.
- **Hint 1:** The reporter says it works with a list and fails with the job's input. What type does `load_jsonl` return?
- **Hint 2:** How many times is `annotations` iterated inside `build_consensus`?
- **Fix:** Add `annotations = list(annotations)` at the top (the docstring even promises generators are supported).
- **Interview move:** Reproduce it with `build_consensus(iter_annotations(lines))` in a new test, watch it fail, then fix.
