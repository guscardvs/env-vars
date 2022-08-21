import functools
import pathlib
import typing

from config.exceptions import InvalidCast, MissingName

from .config import MISSING, Config
from .enums import Env

StrOrPath = str | pathlib.Path
EnvValidator = typing.Callable[[Env], bool]

# Using tuples with integers to prevent bugs with sorting
ENV_RELEVANCE = {Env.TEST: 0, Env.LOCAL: 1, Env.DEV: 2, Env.PRD: 3}


def by_relevance(expected: Env) -> EnvValidator:
    max_relevance = ENV_RELEVANCE[expected]

    def _validator(env: Env):
        return ENV_RELEVANCE[env] <= max_relevance

    return _validator


class EnvConfig(Config):
    def __init__(
        self,
        env_name: str = 'ENV',
        validate_env: EnvValidator = by_relevance(Env.LOCAL),
        env_file: StrOrPath = '.env',
        mapping: typing.Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(env_file)
        self._mapping = mapping or self._mapping
        self._env_name = env_name
        self._validator = validate_env
        self._env = self._preload_env()

    def _preload_env(self) -> Env:
        try:
            return Env(self._mapping[self._env_name])
        except KeyError:
            raise MissingName(self._env_name) from None
        except ValueError:
            raise InvalidCast(
                f'Invalid Env value, expected {", ".join(Env.iter())}'
            ) from None

    @property
    def env(self) -> Env:
        return self._env

    @functools.cached_property
    def consider_file(self):
        return self._validator(self.env)

    def _get_value(self, name: str, default: typing.Any) -> str:
        value = self._mapping.get(name, MISSING)
        if self.consider_file and value is MISSING:
            value = self._file_vals.get(name, default)
        if value is MISSING:
            raise MissingName(name)
        return typing.cast(str, value)
