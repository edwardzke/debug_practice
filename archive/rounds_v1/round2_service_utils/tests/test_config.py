import pytest

from svcutils import ServiceConfig, parse_bool


def test_defaults():
    cfg = ServiceConfig.from_env({})
    assert cfg == ServiceConfig()


def test_overrides():
    cfg = ServiceConfig.from_env(
        {"SVC_CACHE_MAXSIZE": "10", "SVC_RATE_PER_SEC": "2.5", "SVC_DEBUG": "yes"}
    )
    assert cfg.cache_maxsize == 10
    assert cfg.rate_per_sec == 2.5
    assert cfg.debug is True


def test_custom_prefix():
    cfg = ServiceConfig.from_env({"X_BURST": "3"}, prefix="X_")
    assert cfg.burst == 3.0


def test_validation():
    with pytest.raises(ValueError):
        ServiceConfig.from_env({"SVC_RETRY_ATTEMPTS": "0"})


@pytest.mark.parametrize("raw,expected", [("1", True), ("Off", False), (" TRUE ", True), ("", False)])
def test_parse_bool(raw, expected):
    assert parse_bool(raw) is expected


def test_parse_bool_rejects_garbage():
    with pytest.raises(ValueError):
        parse_bool("maybe")
