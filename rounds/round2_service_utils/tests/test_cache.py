import pytest

from svcutils import TTLCache


def test_set_and_get(clock):
    c = TTLCache(maxsize=4, ttl=10, clock=clock)
    c.set("a", 1)
    assert c.get("a") == 1
    assert c.get("missing", "dflt") == "dflt"
    assert c.stats.hits == 1
    assert c.stats.misses == 1


def test_invalid_args():
    with pytest.raises(ValueError):
        TTLCache(maxsize=0)
    with pytest.raises(ValueError):
        TTLCache(ttl=0)


def test_evicts_oldest_when_full(clock):
    c = TTLCache(maxsize=2, ttl=10, clock=clock)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    assert "a" not in c
    assert c.get("b") == 2 and c.get("c") == 3
    assert c.stats.evictions == 1


def test_get_refreshes_recency(clock):
    c = TTLCache(maxsize=2, ttl=10, clock=clock)
    c.set("a", 1)
    c.set("b", 2)
    c.get("a")
    c.set("c", 3)
    assert "a" in c
    assert "b" not in c


def test_overwrite_refreshes_recency(clock):
    c = TTLCache(maxsize=2, ttl=10, clock=clock)
    c.set("a", 1)
    c.set("b", 2)
    c.set("a", 100)
    c.set("c", 3)
    assert c.get("a") == 100
    assert "b" not in c


def test_entries_expire(clock):
    c = TTLCache(maxsize=4, ttl=10, clock=clock)
    c.set("a", 1)
    clock.advance(9.99)
    assert c.get("a") == 1
    clock.advance(0.01)
    assert c.get("a") is None
    assert len(c) == 0


def test_per_entry_ttl(clock):
    c = TTLCache(maxsize=4, ttl=10, clock=clock)
    c.set("short", 1, ttl=1)
    c.set("long", 2)
    clock.advance(5)
    assert "short" not in c
    assert "long" in c
    assert c.purge_expired() == 1


def test_delete(clock):
    c = TTLCache(clock=clock)
    c.set("a", 1)
    assert c.delete("a") is True
    assert c.delete("a") is False


def test_hit_rate(clock):
    c = TTLCache(clock=clock)
    assert c.stats.hit_rate == 0.0
    c.set("a", 1)
    c.get("a")
    c.get("a")
    c.get("b")
    assert c.stats.hit_rate == pytest.approx(2 / 3)
