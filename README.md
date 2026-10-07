# Debugging Round Practice

Three timed practice rounds modeled on a "debugging round" interview: an unfamiliar small Python
codebase, a red test suite, a bug report with no test, and about 45 minutes.

| # | Round | Theme | Bugs |
|---|-------|-------|------|
| 1 | `round1_task_queue` | priority queue + scheduler that hands labeling tasks to labelers | 6 |
| 2 | `round2_service_utils` | LRU/TTL cache, token-bucket rate limiter, retry decorator | 7 |
| 3 | `round3_annotation_pipeline` | JSONL parsing, bbox IoU, majority-vote consensus | 6 |

Each round has one bug that **only** appears in the `BRIEF.md` bug report. No test catches it, so
you have to reproduce it yourself, ideally by writing a failing test first.

## Setup (once)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Running a round
```bash
python practice.py list                # rounds + status
python practice.py start 1             # copies a fresh buggy round to workspace/round1, starts a 45-min timer
python practice.py start 1 --minutes 60
python practice.py check 1             # run tests, show N/M passing and elapsed time
python practice.py check 1 -x -k heap  # extra args go to pytest
python practice.py reset 1             # throw away workspace/round1 to try again later
```
Edit files **only in `workspace/roundN/`**. `rounds/` holds the pristine buggy copies.

## Rules to simulate the interview
- Don't open `solutions/` until time is up (or you're stuck; the hints are tiered, so read one line at a time).
- Don't edit the tests. Adding new tests is encouraged.
- **Talk out loud** (or record yourself). Interviewers grade your process as much as the fixes.
- Use whatever you'd have in an interview: `pytest -x`, `pytest -k`, `print`, `breakpoint()`, a REPL.

## A process that works
1. **Survey (3–5 min):** Read the BRIEF and skim each module's docstrings. Run the tests and count failures by file.
2. **Triage:** Group the failures. Many failures in unrelated tests usually means one root cause in a lower layer, so start at the bottom of the import graph.
3. **One bug at a time:** Pick one failing test (`pytest -x -k name`), read the assertion, form a hypothesis, check it with the smallest experiment, fix it, and **re-run everything**.
4. **Watch for cascades:** Fixing one bug can expose another, or change how a test fails. That counts as progress.
5. **Bug report:** Turn the ticket into a failing test, then fix it.
6. **Narrate:** "I expect X because the docstring says Y; I see Z; so the bug is between here and here."

## After a round
Read `solutions/roundN.md`. For each bug you missed, write down which signal you overlooked:
a docstring, a traceback line, or a test that passed by coincidence.

## Maintainer
`python practice.py verify all` checks that each pristine round fails, that the bug-report test
(`solutions/hidden_tests/`) fails, and that `solutions/roundN.patch` turns everything green.
