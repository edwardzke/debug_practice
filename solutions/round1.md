# Round 1 Solutions — Labeling Task Queue (SPOILERS)

6 bugs: 5 caught by tests, 1 only in the bug report. Reference fix: `round1.patch`.

**Triage tip:** 16 of 32 tests fail at first, and several fail with `AttributeError: 'NoneType'...`
in scheduler tests that look unrelated. Many failures with one shared root cause is a signal to fix the lowest layer first
(models, then queue, then scheduler) and re-run after every fix.

---

## Bug 1 — Mutable default argument (`models.py`, `Task.__init__`)
**Symptom:** `test_tags_are_independent_between_tasks`, `test_task_copies_tag_list`, plus scheduler tests that
return `None` when a task should have been assigned. Results can change with test order.
- **Hint 1:** Add a tag to one task, then print a different, freshly created task's tags.
- **Hint 2:** Look at the default value of `tags` in `__init__`. When is it evaluated?
- **Fix:** `tags: list[str] | None = None` and `self.tags = list(tags) if tags is not None else []`.
- **Why:** Default values are evaluated once, when the function is defined, so every `Task()` shares one list.
  Assigning the caller's list directly also aliases it, which is why `test_task_copies_tag_list` fails.

## Bug 2 — Capacity off-by-one (`models.py`, `Labeler.has_capacity`)
**Symptom:** `test_labeler_capacity_limit`, `test_assign_respects_capacity`: a labeler with capacity 1 gets 2 tasks.
- **Hint 1:** With `capacity=2` and 2 active tasks, what does `has_capacity()` return?
- **Fix:** `<=` → `<`.

## Bug 3 — Inverted heap priority (`queue.py`, `push`)
**Symptom:** `test_higher_priority_pops_first`: the lowest priority comes out first.
- **Hint 1:** `heapq` is a *min*-heap. The docstring says higher priority should come out first.
- **Hint 2:** Look at the first element of the entry tuple.
- **Fix:** `entry = [-task.priority, task.created_at, next(self._counter), task]`.
- **Note:** The counter keeps `Task` objects out of comparisons (they aren't orderable) and gives FIFO order on exact ties.

## Bug 4 — Dict mutated while iterating (`scheduler.py`, `expire_stale`)
**Symptom:** `RuntimeError: dictionary changed size during iteration`. It only appears after Bugs 1–3 are fixed (cascade).
- **Hint 1:** Read the traceback: which line deletes from the dict you're looping over?
- **Fix:** `for task_id, task in list(self.in_flight.items()):`, i.e. iterate over a snapshot.

## Bug 5 — Timeout boundary (`scheduler.py`, `expire_stale`)
**Symptom:** `test_task_expires_exactly_at_timeout`.
- **Hint 1:** The class docstring says a task is stale once it has been held "for `timeout_s` seconds **or more**".
- **Fix:** `>` → `>=`.

## Bug 6 (bug report OPS-2291) — Floor division (`metrics.py`, `throughput_per_hour`)
**Symptom:** 3 tasks in 2 hours shows 1.0 instead of 1.5. The existing tests use whole-number answers, so they pass.
- **Hint 1:** Write the test from the ticket first (3 completions, a 7200-second window, expect 1.5).
- **Fix:** `count // hours` → `count / hours`.
- **Interview move:** Reproduce the bug with a failing test *before* fixing it, and say that out loud.

## Red herrings
`average_handle_time`, `labeler_utilization`, `summary`, `complete` and
`TaskQueue.remove/peek` are all correct. If you "fixed" one of them, ask yourself which test or spec justified the change.
