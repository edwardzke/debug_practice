# Round 2 Solutions — Service Utilities (SPOILERS)

7 bugs: 6 caught by tests, 1 only in the bug report. Reference fix: `round2.patch`.
`config.py` is bug-free (red herring).

---

## Bug 1 — LRU `get` doesn't refresh recency (`cache.py`, `get`)
**Symptom:** `test_get_refreshes_recency`: the entry that was just read gets evicted.
- **Hint 1:** In an `OrderedDict`-based LRU, which end holds the least recently used entry, and what moves an entry to the other end?
- **Hint 2:** Compare `set` with `get`.
- **Fix:** Call `self._data.move_to_end(key)` on a hit in `get`.

## Bug 2 — TTL uses the wall clock, not the injected clock (`cache.py`, `set`)
**Symptom:** `test_entries_expire`, `test_per_entry_ttl`: entries never expire under the fake clock.
- **Hint 1:** Print `expires_at` in a test. The fake clock starts at 0.
- **Hint 2:** `get` checks expiry with `self._clock()`. What does `set` use?
- **Fix:** `expires_at = self._clock() + ...`.
- **Why it matters:** Mixing time sources is a classic production bug: it breaks testability and is wrong when clocks differ (monotonic vs wall time).

## Bug 3 — Token refill truncated (`ratelimit.py`, `_refill`)
**Symptom:** `test_refill_accumulates_small_steps`: refilling at 2 tokens/s in 0.25 s steps never adds anything.
`test_refills_over_time` passes because 0.5 s × 2 = exactly 1.
- **Hint 1:** What is `int(0.25 * 2)`? And `_last` advances anyway...
- **Fix:** `self._tokens + elapsed * self.rate` (no `int`).
- **Why:** The time is consumed (`_last = now`) but the fractional tokens are thrown away, so frequent callers starve.

## Bug 4 — Class-level mutable state (`ratelimit.py`, `RateLimiterRegistry`)
**Symptom:** `test_registries_do_not_share_buckets`: the paid tier gets the free tier's bucket.
- **Hint 1:** Where is `_buckets` defined? Is it per instance?
- **Fix:** Delete the class attribute and set `self._buckets = {}` in `__init__`.

## Bug 5 — Retry off-by-one (`retry.py`)
**Symptom:** `test_recovers_on_last_attempt` / `test_delay_is_capped` return `None`;
`test_raises_after_exhausting_attempts` raises nothing at all.
- **Hint 1:** With `max_attempts=3`, how many times does `range(1, max_attempts)` loop?
- **Hint 2:** What does the function return when the loop just ends?
- **Fix:** `range(1, max_attempts + 1)`. The reference also adds `raise AssertionError("unreachable")` after the loop so this mistake can never fail silently again.

## Bug 6 — Retries non-retryable errors (`retry.py`)
**Symptom:** `test_non_retryable_error_propagates_immediately`: a `ValueError` is retried. This is a cascade: before Bug 5 is fixed it fails differently.
- **Hint 1:** What does the `except` clause catch, and what is `retry_on` used for?
- **Fix:** `except retry_on:`.
- **Why:** Retrying a bad request or a programming error wastes time and hides bugs.

## Bug 7 (bug report INFRA-877) — Missing `functools.wraps` (`retry.py`)
**Symptom:** Decorated functions are named `wrapper` and have no docstring. The unused `import functools` is the clue.
- **Hint 1:** In a REPL: `retry()(some_fn).__name__`.
- **Fix:** Put `@functools.wraps(fn)` on `wrapper`.
- **Interview move:** Write the test first: assert on `__name__` and `__doc__`.
