# Round 2 — Service Utilities

`svcutils` is a small internal library that every backend service imports
for caching, rate limiting and retries. Someone "simplified" it, and now
several services report odd behavior. The test suite is red.

**Package:** `svcutils/`
- `cache.py` — LRU cache with a per-entry TTL and an injectable clock
- `ratelimit.py` — token bucket plus a per-customer registry
- `retry.py` — retry decorator with exponential backoff
- `config.py` — loads settings from environment variables

Docstrings describe the **intended** behavior. Tests are correct; do not
edit them (you may *add* tests).

## Your job
1. Get `pytest` green.
2. Handle this bug report, which has **no failing test**:

> **INFRA-877** — "Since the svcutils upgrade, every function we decorate
> with `@retry` shows up as `wrapper` in our tracing and metrics, and
> `help()` on them prints nothing useful. Our per-endpoint dashboards have
> collapsed into one line called `wrapper`."

Talk through your reasoning out loud as you go.

Run tests: `python ../../practice.py check 2` (from here) or `python -m pytest -q`.
