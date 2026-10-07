"""Retry decorator with exponential backoff."""

from __future__ import annotations

import functools
import time
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def retry(
    max_attempts: int = 3,
    base_delay: float = 0.1,
    backoff: float = 2.0,
    max_delay: float = 10.0,
    retry_on: tuple[type[BaseException], ...] = (ConnectionError, TimeoutError),
    sleep: Callable[[float], None] = time.sleep,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Call the wrapped function up to ``max_attempts`` times in total.

    Only exceptions that are instances of ``retry_on`` trigger a retry; any
    other exception propagates immediately. If the final attempt fails, its
    exception is re-raised. Delays between attempts are ``base_delay``,
    ``base_delay * backoff``, ... capped at ``max_delay``.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            delay = base_delay
            for attempt in range(1, max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts:
                        raise
                    sleep(min(delay, max_delay))
                    delay *= backoff

        return wrapper

    return decorator
