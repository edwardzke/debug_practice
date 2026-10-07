"""Service configuration loaded from environment variables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off", ""}


def parse_bool(raw: str) -> bool:
    value = raw.strip().lower()
    if value in _TRUE:
        return True
    if value in _FALSE:
        return False
    raise ValueError(f"not a boolean: {raw!r}")


@dataclass(frozen=True)
class ServiceConfig:
    cache_maxsize: int = 256
    cache_ttl: float = 30.0
    rate_per_sec: float = 5.0
    burst: float = 10.0
    retry_attempts: int = 3
    debug: bool = False

    @classmethod
    def from_env(cls, env: Mapping[str, str], prefix: str = "SVC_") -> "ServiceConfig":
        def get(name: str) -> str | None:
            return env.get(prefix + name)

        kwargs: dict[str, object] = {}
        if (v := get("CACHE_MAXSIZE")) is not None:
            kwargs["cache_maxsize"] = int(v)
        if (v := get("CACHE_TTL")) is not None:
            kwargs["cache_ttl"] = float(v)
        if (v := get("RATE_PER_SEC")) is not None:
            kwargs["rate_per_sec"] = float(v)
        if (v := get("BURST")) is not None:
            kwargs["burst"] = float(v)
        if (v := get("RETRY_ATTEMPTS")) is not None:
            kwargs["retry_attempts"] = int(v)
        if (v := get("DEBUG")) is not None:
            kwargs["debug"] = parse_bool(v)
        cfg = cls(**kwargs)  # type: ignore[arg-type]
        cfg.validate()
        return cfg

    def validate(self) -> None:
        if self.cache_maxsize < 1:
            raise ValueError("cache_maxsize must be >= 1")
        if self.burst < 1:
            raise ValueError("burst must be >= 1")
        if self.retry_attempts < 1:
            raise ValueError("retry_attempts must be >= 1")
