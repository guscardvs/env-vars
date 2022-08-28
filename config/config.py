import os
import pathlib
import typing

from .exceptions import InvalidCast, MissingName
from .mapping import EnvMapping, LowerEnvMapping


class MISSING:
    pass


StrOrPath = str | pathlib.Path
AnyCallable = typing.Callable[[str], typing.Any]
CastType = type | AnyCallable
T = typing.TypeVar('T')

environ = EnvMapping()


class Config:
    def __init__(
        self,
        env_file: StrOrPath | None = None,
        mapping: typing.Mapping[str, str] = environ,
    ) -> None:
        self._mapping = mapping
        self._file_vals: typing.Dict[str, str] = {}
        if env_file is not None and os.path.isfile(env_file):
            self._file_vals = self._load_file(env_file)

    def _load_file(self, env_file: StrOrPath) -> typing.Dict[str, str]:
        output = {}
        with open(env_file) as stream:
            for line in stream:
                if line.startswith('#') or '=' not in line:
                    continue
                name, value = line.split('=', 1)
                output[name.strip()] = value.strip()
        return output

    def _get_value(self, name: str, default: typing.Any) -> str:
        value = self._mapping.get(name, self._file_vals.get(name, default))
        if value is MISSING:
            raise MissingName(name)
        return value

    def _cast(
        self, name: str, value: typing.Any, cast: CastType,
    ) -> typing.Any:
        try:
            return cast(value)
        except (TypeError, ValueError) as err:
            raise InvalidCast(
                f"Config '{name}' has value '{value}'."
                f' Not a valid {cast.__name__}.'
            ) from err

    def get(
        self,
        name: str,
        cast: AnyCallable | None = None,
        default: typing.Any = MISSING,
    ) -> typing.Any:
        value = self._get_value(name, default)
        return value if cast is None else self._cast(name, value, cast)

    @typing.overload
    def __call__(
        self,
        name: str,
        cast: typing.Callable[[str], T],
        default: typing.Any = MISSING,
    ) -> T:
        ...

    @typing.overload
    def __call__(
        self, name: str, cast: None = None, default: typing.Any = MISSING,
    ) -> str:
        ...

    def __call__(
        self,
        name: str,
        cast: AnyCallable | None = None,
        default: typing.Any = MISSING,
    ) -> typing.Any:
        return self.get(name, cast, default)


class CachedConfig(Config):
    def __init__(
        self,
        env_file: typing.Optional[StrOrPath] = None,
        mapping: typing.Mapping[str, str] = environ,
    ) -> None:
        super().__init__(env_file, mapping)
        self._cached: dict[str, typing.Any] = {}

    def get(
        self,
        name: str,
        cast: AnyCallable | None = None,
        default: typing.Any = MISSING,
    ) -> typing.Any:
        try:
            return self._cached[name]
        except KeyError:
            return self._cached.setdefault(
                name, super().get(name, cast, default)
            )


lower_environ = LowerEnvMapping(environ)


class CIConfig(Config):
    """Case Insensitive Config"""

    def __init__(
        self,
        env_file: StrOrPath | None = None,
        mapping: typing.Mapping[str, str] = lower_environ,
    ) -> None:
        super().__init__(env_file, mapping)

    def get(
        self,
        name: str,
        cast: AnyCallable | None = None,
        default: typing.Any = MISSING,
    ) -> typing.Any:
        return super().get(name.lower(), cast, default)
