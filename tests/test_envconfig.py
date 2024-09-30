from pathlib import Path

import pytest

from config.config import EnvMapping
from config.enums import Env
from config.envconfig import DotFile, EnvConfig
from config.exceptions import InvalidCast, MissingName

PARENT_DIR = curpath = Path(__file__).resolve().parent


def test_envconfig_returns_file_vals_if_in_expected_env():
    """EnvConfig should consider file_vals
    if env matches consider_file_on_env"""
    environ = EnvMapping({"CONFIG_ENV": Env.LOCAL.val})
    config = EnvConfig(DotFile(PARENT_DIR / ".envconfig", Env.LOCAL), mapping=environ)

    assert config.env is Env.LOCAL
    assert config("NAME") == "teste"


def test_envconfig_does_not_find_value_if_not_in_expected_env():
    environ = EnvMapping({"CONFIG_ENV": Env.DEV.val})
    config = EnvConfig(DotFile(PARENT_DIR / ".envconfig", Env.LOCAL), mapping=environ)

    with pytest.raises(MissingName):
        config("NAME")


def test_envconfig_raises_missing_name_if_no_env_is_found():
    with pytest.raises(MissingName):
        EnvConfig(DotFile(PARENT_DIR / ".envconfig", Env.LOCAL))


def test_envconfig_raises_invalid_cast_if_env_val_is_invalid():
    environ = EnvMapping({"CONFIG_ENV": "invalid"})

    with pytest.raises(InvalidCast):
        EnvConfig(
            DotFile(PARENT_DIR / ".envconfig", Env.LOCAL),
            mapping=environ,
        )
