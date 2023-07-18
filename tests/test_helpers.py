import pytest

import config


def test_comma_separated_returns_valid_split():
    mapping = config.EnvMapping({"key": "a, b, c"})
    cfg = config.Config(mapping=mapping)

    val = cfg("key", config.comma_separated())

    assert val == ("a", "b", "c")


def test_comma_separated_returns_valid_split_with_cast():
    mapping = config.EnvMapping({"key": "1, 2, 3"})
    cfg = config.Config(mapping=mapping)
    val = cfg("key", config.comma_separated(int))

    assert val == (1, 2, 3)


def test_boolean_returns_valid_bool():
    mapping = config.EnvMapping(
        {"first": "true", "second": "False", "third": "1", "forth": "0"}
    )
    cfg = config.Config(mapping=mapping)

    assert cfg("first", config.boolean_cast)
    assert not cfg("second", config.boolean_cast)
    assert cfg("third", config.boolean_cast)
    assert not cfg("forth", config.boolean_cast)


def test_boolean_raises_invalid_cast():
    """test boolean raises invalid cast if
    no boolean definition matches"""
    mapping = config.EnvMapping({"key": "value"})
    cfg = config.Config(mapping=mapping)

    with pytest.raises(config.InvalidCast):
        cfg("key", config.boolean_cast.strict)
