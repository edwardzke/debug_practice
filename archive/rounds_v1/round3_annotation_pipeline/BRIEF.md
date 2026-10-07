# Round 3 — Annotation Consensus Pipeline

Several labelers annotate each image (a class label, plus an optional
bounding box). This pipeline merges their submissions into a consensus
label per image, scores how much they agree, and flags items for QA review.
QA says the numbers have been nonsense since the last release. The test
suite is red.

**Package:** `annopipe/`
- `parse.py` — reads JSON Lines submissions (see the module docstring for the format)
- `geometry.py` — bounding-box conversion and IoU
- `consensus.py` — majority vote, agreement, box agreement per item
- `export.py` — CSV export and the review filter

Docstrings describe the **intended** behavior. Tests are correct; do not
edit them (you may *add* tests).

## Your job
1. Get `pytest` green.
2. Handle this bug report, which has **no failing test**:

> **DATA-1450** — "When the nightly job runs on the real file it writes an
> empty consensus CSV, header only. If I load the same file into a list in a
> notebook first and then call `build_consensus`, I get results. The job is
> `build_consensus(load_jsonl(path))`."

Talk through your reasoning out loud as you go.

Run tests: `python ../../practice.py check 3` (from here) or `python -m pytest -q`.
