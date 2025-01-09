from enum import Enum
from pathlib import Path
from typing import Literal

import pytest

import config
from config.exceptions import InvalidCast, InvalidEnv, MissingName
from config.utils import (
    boolean_cast,
    instance_is_casted,
    literal_cast,
    multicast,
    none_is_missing,
)


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
        {"first": "true", "second": "False", "third": "1", "fourth": "0"}
    )
    cfg = config.Config(mapping=mapping)

    assert cfg("first", config.boolean_cast)
    assert not cfg("second", config.boolean_cast)
    assert cfg("third", config.boolean_cast)
    assert not cfg("fourth", config.boolean_cast)
    assert config.boolean_cast.strict(True) is True
    assert config.boolean_cast.strict(False) is False


def test_boolean_raises_invalid_cast():
    """test boolean raises invalid cast if
    no boolean definition matches"""
    mapping = config.EnvMapping({"key": "value"})
    cfg = config.Config(mapping=mapping)

    with pytest.raises(config.InvalidCast):
        cfg("key", config.boolean_cast.strict)


def test_valid_path_returns_path_object(tmp_path: Path):
    filepath = tmp_path / "file.txt"
    filepath.touch()
    mapping = config.EnvMapping({"key": filepath.as_posix()})
    cfg = config.Config(mapping=mapping)

    val = cfg("key", config.valid_path)

    assert isinstance(val, Path)
    assert val == filepath


def test_valid_path_raises_file_not_found_error():
    """test valid_path raises FileNotFoundError
    if the path does not exist."""
    mapping = config.EnvMapping({"key": "./non_existent_file.txt"})
    cfg = config.Config(mapping=mapping)
    valpath = Path("./non_existent_file.txt")

    with pytest.raises(InvalidCast) as exc_info:
        cfg("key", config.valid_path)

    assert isinstance(exc_info.value.__cause__, FileNotFoundError)
    assert exc_info.value.__cause__.args == (
        f"Path {valpath!s} is not valid path",
        valpath,
    )


def test_joined_cast_composes_cast_functions():
    mapping = config.EnvMapping({"key": "42"})
    cfg = config.Config(mapping=mapping)

    # Casting sequence: str -> int -> str -> float
    val = cfg("key", config.joined_cast(int).cast(float).cast(str))

    assert isinstance(val, str)
    assert val == "42.0"


def test_with_rule_valid_rule():
    mapping = config.EnvMapping({"key": "42"})
    cfg = config.Config(mapping=mapping)

    # Rule: Value must be greater than 40
    def greater_than_40(x):
        return int(x) > 40

    # Valid rule check (value is greater than 40)
    cfg("key", config.with_rule(greater_than_40))


def test_with_rule_invalid_rule():
    """test with_rule raises InvalidEnv
    if the rule condition is not met."""
    mapping = config.EnvMapping({"key": "42"})
    cfg = config.Config(mapping=mapping)

    # Rule: Value must be less than 40
    def less_than_40(x):
        return int(x) < 40

    # Invalid rule check (value is not less than 40)
    with pytest.raises(InvalidCast) as exc_info:
        cfg("key", config.with_rule(less_than_40))

    assert isinstance(exc_info.value.__cause__, InvalidEnv)
    assert exc_info.value.__cause__.args == (
        f"Value 42 did not pass rule check {less_than_40.__name__}",
        less_than_40,
        "42",
    )


def test_literal_cast_returns_valid_cast():
    class Test(Enum):
        VALUE = "value"

    literal_type = Literal[1, "other", b"another", Test.VALUE, None, False]
    caster = literal_cast(literal_type)
    mapping = config.EnvMapping(
        {
            "first": "other",
            "second": "another",
            "third": "1",
            "fourth": "value",
            "fifth": "null",
            "sixth": "false",
            "seventh": "invalid",
        }
    )
    cfg = config.Config(mapping=mapping)

    assert (
        cfg("first", caster),
        cfg("second", caster),
        cfg("third", caster),
        cfg("fourth", caster),
        cfg("fifth", caster),
        cfg("sixth", caster),
    ) == (
        "other",
        b"another",
        1,
        Test.VALUE,
        None,
        False,
    )

    with pytest.raises(InvalidCast) as exc_info:
        cfg("seventh", caster)

    assert exc_info.value.__cause__.args == (  # type: ignore
        "Value received does not match any argument from literal",
        literal_type.__args__,  # type: ignore
    )


def test_none_is_missing():
    mapping = config.EnvMapping({"key": "null"})
    cfg = config.Config(mapping=mapping)

    with pytest.raises(MissingName):
        cfg("key", none_is_missing(boolean_cast.optional))


def test_multicast():
    def surely_fails(val):
        raise ValueError("This function does not work")

    def returns_anything(val):
        return "anything"

    mapping = config.EnvMapping({"key": "42"})
    cfg = config.Config(mapping=mapping)

    assert cfg("key", multicast(int, surely_fails)) == 42

    with pytest.raises(InvalidCast) as exc_info:
        cfg("key", multicast(boolean_cast.strict, surely_fails))
    assert exc_info.value.__cause__.args == ("This function does not work",)

    assert cfg("key", multicast(returns_anything, surely_fails)) == "anything"


def test_instance_is_casted():
    missing = object()

    caster = instance_is_casted(str, lambda _: missing)

    assert caster("hello") == "hello"
    assert caster(123) is missing
