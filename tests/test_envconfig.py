from pathlib import Path

import pytest

from config.enums import Env
from config.envconfig import EnvConfig
from config.exceptions import InvalidCast
from config.exceptions import MissingName
from config.mapping import EnvMapping

PARENT_DIR = curpath = Path(__file__).resolve().parent


def test_envconfig_returns_file_vals_if_in_expected_env():
    """EnvConfig should consider file_vals
    if env matches consider_file_on_env"""
    environ = EnvMapping({'ENV': Env.LOCAL})
    config = EnvConfig(env_file=PARENT_DIR / '.envconfig', mapping=environ)

    assert config.env is Env.LOCAL
    assert config('NAME') == 'teste'


def test_envconfig_does_not_find_value_if_not_in_expected_env():
    environ = EnvMapping({'ENV': Env.DEV})
    config = EnvConfig(env_file=PARENT_DIR / '.envconfig', mapping=environ)

    with pytest.raises(MissingName):
        config('NAME')


def test_envconfig_raises_missing_name_if_no_env_is_found():
    with pytest.raises(MissingName):
        EnvConfig()


def test_envconfig_raises_invalid_cast_if_env_val_is_invalid():
    environ = EnvMapping({'ENV': 'invalid'})

    with pytest.raises(InvalidCast):
        EnvConfig(mapping=environ)
