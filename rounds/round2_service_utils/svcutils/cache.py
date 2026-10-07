"""In-memory LRU cache with per-entry time-to-live."""

from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Callable, Generic, Hashable, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

_MISSING = object()


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


class TTLCache(Generic[K, V]):
    """Least-recently-used cache whose entries also expire after ``ttl`` seconds.

    * ``get`` counts as a use: it refreshes an entry's recency (not its TTL).
    * When the cache exceeds ``maxsize``, the least recently used entry is evicted.
    * An entry is expired once ``clock() >= expires_at``.
    """

    def __init__(
        self,
        maxsize: int = 128,
        ttl: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if maxsize < 1:
            raise ValueError("maxsize must be >= 1")
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        self.maxsize = maxsize
        self.ttl = ttl
        self._clock = clock
        self._data: OrderedDict[K, tuple[V, float]] = OrderedDict()
        self.stats = CacheStats()

    def _expired(self, expires_at: float) -> bool:
        return self._clock() >= expires_at

    def get(self, key: K, default: V | None = None) -> V | None:
        item = self._data.get(key, _MISSING)
        if item is _MISSING:
            self.stats.misses += 1
            return default
        value, expires_at = item  # type: ignore[misc]
        if self._expired(expires_at):
            del self._data[key]
            self.stats.misses += 1
            return default
        self.stats.hits += 1
        return value

    def set(self, key: K, value: V, ttl: float | None = None) -> None:
        expires_at = time.monotonic() + (self.ttl if ttl is None else ttl)
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = (value, expires_at)
        while len(self._data) > self.maxsize:
            self._data.popitem(last=False)
            self.stats.evictions += 1

    def delete(self, key: K) -> bool:
        return self._data.pop(key, _MISSING) is not _MISSING

    def purge_expired(self) -> int:
        dead = [k for k, (_, exp) in self._data.items() if self._expired(exp)]
        for k in dead:
            del self._data[k]
        return len(dead)

    def __contains__(self, key: object) -> bool:
        item = self._data.get(key, _MISSING)  # type: ignore[arg-type]
        return item is not _MISSING and not self._expired(item[1])  # type: ignore[index]

    def __len__(self) -> int:
        self.purge_expired()
        return len(self._data)
