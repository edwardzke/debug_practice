import pytest

from svcutils import RateLimiterRegistry, TokenBucket


def test_starts_full(clock):
    b = TokenBucket(rate=1, capacity=3, clock=clock)
    assert [b.try_acquire() for _ in range(4)] == [True, True, True, False]


def test_refills_over_time(clock):
    b = TokenBucket(rate=2, capacity=2, clock=clock)
    assert b.try_acquire(2)
    assert not b.try_acquire()
    clock.advance(0.5)
    assert b.try_acquire()


def test_refill_accumulates_small_steps(clock):
    b = TokenBucket(rate=2, capacity=4, clock=clock)
    assert b.try_acquire(4)
    for _ in range(4):
        clock.advance(0.25)
        b.tokens
    assert b.tokens == pytest.approx(2.0)


def test_refill_capped_at_capacity(clock):
    b = TokenBucket(rate=10, capacity=5, clock=clock)
    clock.advance(100)
    assert b.tokens == 5


def test_wait_time(clock):
    b = TokenBucket(rate=4, capacity=4, clock=clock)
    assert b.wait_time() == 0.0
    b.try_acquire(4)
    assert b.wait_time(2) == pytest.approx(0.5)


def test_cannot_acquire_more_than_capacity(clock):
    b = TokenBucket(rate=1, capacity=2, clock=clock)
    with pytest.raises(ValueError):
        b.try_acquire(3)


def test_registry_isolates_keys(clock):
    r = RateLimiterRegistry(rate=1, capacity=1, clock=clock)
    assert r.allow("alice")
    assert not r.allow("alice")
    assert r.allow("bob")
    assert len(r) == 2


def test_registries_do_not_share_buckets(clock):
    free_tier = RateLimiterRegistry(rate=1, capacity=1, clock=clock)
    paid_tier = RateLimiterRegistry(rate=100, capacity=50, clock=clock)
    assert free_tier.allow("acme")
    assert paid_tier.bucket("acme").capacity == 50
    assert paid_tier.allow("acme")
    assert len(free_tier) == 1
    assert len(paid_tier) == 1
