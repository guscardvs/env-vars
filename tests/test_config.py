import string

import pytest
from hypothesis import given
from hypothesis.strategies import integers
from hypothesis.strategies import text

import config


@given(text(), text())
def test_config_call_success(key: str, value: str):
    """test config call returns valid string
    from mapping source when name exists"""
    mapping = config.EnvMapping({key: value})
    cfg = config.Config(mapping=mapping)

    val = cfg(key)

    assert isinstance(val, str)
    assert val == value


def test_config_call_name_not_found():
    """test config call raises `config.MissingName`
    if name does not exists in source mapping"""
    mapping = config.EnvMapping({})
    cfg = config.Config(mapping=mapping)

    with pytest.raises(config.MissingName):
        cfg('invalid')


def test_config_cast_returns_cast_type():
    """test config cast returns cast type
    when name exists"""

    class _Cast:
        def __init__(self, val: str) -> None:
            self.val = val

    key = 'key'
    value = 'val'
    mapping = config.EnvMapping({key: value})
    cfg = config.Config(mapping=mapping)

    casted = cfg(key, _Cast)

    assert isinstance(casted, _Cast)
    assert casted.val == value


def test_config_cast_fails_with_invalid_cast():
    """test config cast fails with invalid cast
    when cast raises TypeError or ValueError"""

    def _fail_cast(val: str):
        raise TypeError

    mapping = config.EnvMapping({'key': 'value'})
    cfg = config.Config(mapping=mapping)

    with pytest.raises(config.InvalidCast):
        cfg('key', _fail_cast)


@given(text(), integers())
def test_cached_config_executes_only_once(key: str, value: int):
    """test cached config searches and casts
    only on the first call"""
    mapping = config.EnvMapping({key: value})
    cfg = config.CachedConfig(mapping=mapping)

    assert str(value) == cfg(key, str)
    assert str(value) == cfg(key, bool)


@given(
    text().filter(
        lambda item: all(map(lambda char: char in string.ascii_letters, item))
    ),
    integers(),
)
def test_ci_config_matches_insensitively(key: str, value: int):
    mapping = config.LowerEnvMapping({key: str(value)})
    cfg = config.CIConfig(mapping=mapping)

    assert value == cfg(key.upper(), int)
