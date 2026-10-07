"""Token-bucket rate limiting."""

from __future__ import annotations

import time
from typing import Callable


class TokenBucket:
    """Classic token bucket.

    The bucket holds at most ``capacity`` tokens and refills continuously at
    ``rate`` tokens per second. It starts full.
    """

    def __init__(
        self,
        rate: float,
        capacity: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if rate <= 0 or capacity <= 0:
            raise ValueError("rate and capacity must be positive")
        self.rate = rate
        self.capacity = capacity
        self._clock = clock
        self._tokens = float(capacity)
        self._last = clock()

    def _refill(self) -> None:
        now = self._clock()
        elapsed = now - self._last
        if elapsed > 0:
            self._tokens = min(self.capacity, self._tokens + int(elapsed * self.rate))
            self._last = now

    @property
    def tokens(self) -> float:
        self._refill()
        return self._tokens

    def try_acquire(self, n: float = 1) -> bool:
        if n > self.capacity:
            raise ValueError("cannot acquire more tokens than capacity")
        self._refill()
        if self._tokens >= n:
            self._tokens -= n
            return True
        return False

    def wait_time(self, n: float = 1) -> float:
        """Seconds until ``n`` tokens will be available (0 if available now)."""
        self._refill()
        deficit = n - self._tokens
        return max(0.0, deficit / self.rate)


class RateLimiterRegistry:
    """Lazily creates one bucket per key (e.g. per API customer)."""

    _buckets: dict[str, TokenBucket] = {}

    def __init__(
        self,
        rate: float,
        capacity: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.rate = rate
        self.capacity = capacity
        self._clock = clock

    def bucket(self, key: str) -> TokenBucket:
        if key not in self._buckets:
            self._buckets[key] = TokenBucket(self.rate, self.capacity, self._clock)
        return self._buckets[key]

    def allow(self, key: str, n: float = 1) -> bool:
        return self.bucket(key).try_acquire(n)

    def __len__(self) -> int:
        return len(self._buckets)
