import pathlib
import typing

from config.exceptions import InvalidCast, MissingName

from .config import Config
from .enums import Env

StrOrPath = str | pathlib.Path


class EnvConfig(Config):
    def __init__(
        self,
        env_name: str = 'ENV',
        consider_file_on_env: Env = Env.LOCAL,
        env_file: StrOrPath = '.env',
        mapping: typing.Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(env_file)
        self._mapping = mapping or self._mapping
        self._env_name = env_name
        self._consider_file_on_env = consider_file_on_env
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

    def _get_value(self, name: str, default: typing.Any) -> str:
        value = self._mapping.get(name, None)
        if self._consider_file_on_env is self.env and value is None:
            value = self._file_vals.get(name, default)
        if value is None:
            raise MissingName(name)
        return value
