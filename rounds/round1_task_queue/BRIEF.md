# Round 1 — Labeling Task Queue

You've joined the team that runs the queue handing labeling tasks to human
labelers. The service was "refactored" last sprint and things have been
going wrong in production ever since. The test suite is red.

**Package:** `taskqueue/`
- `models.py` — `Task` and `Labeler`
- `queue.py` — priority queue of pending tasks
- `scheduler.py` — assigns tasks to labelers, reclaims tasks that time out
- `metrics.py` — numbers for the ops dashboard

Read the docstrings: they describe the **intended** behavior. Tests are
correct; do not edit them (you may *add* tests).

## Your job
1. Get `pytest` green.
2. Handle this bug report, which has **no failing test**:

> **OPS-2291** — "The throughput widget looks wrong. Yesterday we finished 3
> tasks in a 2-hour window and the dashboard said 1.0 tasks/hour. It never
> seems to show anything other than whole numbers."

Talk through your reasoning out loud as you go, as you would in the interview.

Run tests: `python ../../practice.py check 1` (from here) or `python -m pytest -q`.
