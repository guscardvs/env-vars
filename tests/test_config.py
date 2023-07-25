from pathlib import Path
import tempfile
import pytest
from hypothesis import given
from hypothesis.strategies import text

import config
from config.exceptions import MissingName


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
        cfg("invalid")


def test_config_cast_returns_cast_type():
    """test config cast returns cast type
    when name exists"""

    class _Cast:
        def __init__(self, val: str) -> None:
            self.val = val

    key = "key"
    value = "val"
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

    mapping = config.EnvMapping({"key": "value"})
    cfg = config.Config(mapping=mapping)

    with pytest.raises(config.InvalidCast):
        cfg("key", _fail_cast)


def test_env_mapping_raises_errors_correctly_on_read():
    mapping = config.EnvMapping({})
    mapping["my-name"] = "val"
    mapping["my-name"]

    with pytest.raises(KeyError):
        mapping["my-name"] = "error"
    with pytest.raises(KeyError):
        del mapping["my-name"]


def test_config_reads_from_env_file(tmp_path: Path):
    filename = tmp_path / ".envtestfile"
    with open(filename, "w") as buf:
        buf.writelines(
            map(
                lambda val: f"{val}\n",
                [
                    "HELLO=world",
                    "# EMAIL=error",
                    "TEST='123abc'",
                    'TESTB=" 321 "',
                    "TESTC=\"'123'\"",
                    "TESTD=abc # comment",
                    "TESTE='abc #comment'",
                    "TESTF=abc#comment",
                    "TESTG='abc' #\"comment\"",
                    "TESTH='abc #comment\"",
                ],
            )
        )
    cfg = config.Config(filename)
    assert cfg("HELLO") == "world"
    assert cfg("TEST") == "123abc"
    assert cfg("TESTB") == " 321 "
    assert cfg("TESTC") == "'123'"
    assert cfg("TESTD") == "abc"
    assert cfg("TESTE") == "abc #comment"
    assert cfg("TESTF") == "abc#comment"
    assert cfg("TESTG") == "abc"
    assert cfg("TESTH") == "'abc"

    with pytest.raises(MissingName):
        cfg("EMAIL")
