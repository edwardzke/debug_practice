import pytest

from svcutils import retry


class Flaky:
    """Fails with ``exc`` for the first ``failures`` calls, then returns 'ok'."""

    def __init__(self, failures, exc=ConnectionError):
        self.failures = failures
        self.exc = exc
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.calls <= self.failures:
            raise self.exc(f"failure #{self.calls}")
        return "ok"


def test_returns_immediately_on_success():
    sleeps = []
    fn = Flaky(0)
    assert retry(sleep=sleeps.append)(fn)() == "ok"
    assert fn.calls == 1
    assert sleeps == []


def test_recovers_on_last_attempt():
    sleeps = []
    fn = Flaky(2)
    wrapped = retry(max_attempts=3, base_delay=1, backoff=2, sleep=sleeps.append)(fn)
    assert wrapped() == "ok"
    assert fn.calls == 3
    assert sleeps == [1, 2]


def test_raises_after_exhausting_attempts():
    fn = Flaky(10)
    wrapped = retry(max_attempts=3, sleep=lambda s: None)(fn)
    with pytest.raises(ConnectionError, match="failure #3"):
        wrapped()
    assert fn.calls == 3


def test_non_retryable_error_propagates_immediately():
    sleeps = []
    fn = Flaky(1, exc=ValueError)
    wrapped = retry(max_attempts=5, sleep=sleeps.append)(fn)
    with pytest.raises(ValueError):
        wrapped()
    assert fn.calls == 1
    assert sleeps == []


def test_delay_is_capped():
    sleeps = []
    fn = Flaky(4)
    wrapped = retry(
        max_attempts=5, base_delay=1, backoff=10, max_delay=5, sleep=sleeps.append
    )(fn)
    assert wrapped() == "ok"
    assert sleeps == [1, 5, 5, 5]


def test_rejects_zero_attempts():
    with pytest.raises(ValueError):
        retry(max_attempts=0)


def test_passes_arguments_through():
    @retry(sleep=lambda s: None)
    def add(a, b, *, c=0):
        return a + b + c

    assert add(1, 2, c=3) == 6
