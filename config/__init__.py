import os
import pathlib
import typing

StrOrPath = typing.Union[str, pathlib.Path]


MISSING = object()
T = typing.TypeVar('T')

AnyCallable = typing.Callable[[typing.Any], typing.Any]
CastType = type | AnyCallable


class AlreadySet(Exception):
    pass


class MissingName(KeyError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Config '{name}' is missing, and has no default.")


class MissingNames(KeyError):
    def __init__(self, names: list[str]) -> None:
        super().__init__(
            f"Config keys {', '.join(names)!r} are missing, and has no default."
        )


class InvalidCast(ValueError):
    pass


class EnvMapping(typing.MutableMapping):
    def __init__(self, environ: typing.MutableMapping = os.environ):
        self._environ = environ
        self._has_been_read: typing.Set[typing.Any] = set()

    def __getitem__(self, key: typing.Any) -> typing.Any:
        self._has_been_read.add(key)
        return self._environ.__getitem__(key)

    def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
        if key in self._has_been_read:
            raise AlreadySet(
                f"Cannot set environ['{key}'], value has already been " 'read.'
            )
        self._environ.__setitem__(key, value)

    def __delitem__(self, key: typing.Any) -> None:
        if key in self._has_been_read:
            raise AlreadySet(
                f"Cannot delete environ['{key}'], value has already "
                'been read.'
            )
        self._environ.__delitem__(key)

    def __iter__(self) -> typing.Iterator:
        return iter(self._environ)

    def __len__(self) -> int:
        return len(self._environ)


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
                f"Config '{name}' has value '{value}'. Not a valid {cast.__name__}."
            ) from err

    def get(
        self,
        name: str,
        cast: AnyCallable | None = None,
        default: typing.Any = MISSING,
    ) -> typing.Any:
        value = self._get_value(name, default)
        if cast is None:
            return value
        return self._cast(name, value, cast)

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
