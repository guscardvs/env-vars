from collections.abc import Sequence as AbstractSequence
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Mapping
from typing import Sequence
from typing import TypeVar
from typing import Union
from typing import get_args
from typing import get_origin
from typing import overload
import typing

from config.exceptions import MissingName
from config.helpers import comma_separated

from .config import MISSING
from .config import Config

T = TypeVar('T')

FieldTuple = tuple[str, Union[type, Callable[[Any], Any]], Union[Any, None]]


@dataclass(frozen=True)
class DeclarativeConfig:
    prefix: str = ''
    no_prefix: Sequence[str] = ()
    parser: Callable[[str], str] = str.upper
    defaults: Mapping[str, Any] = field(default_factory=dict)


_default_config = Config()
_default_decl_config = DeclarativeConfig()


@overload
def declarative(
    cls: type[T],
    /,
    *,
    config: Union[Config, None] = None,
    decl_config: Union[DeclarativeConfig, None] = None,
) -> type[T]:
    ...


@overload
def declarative(
    cls: None = None,
    /,
    *,
    config: Union[Config, None] = None,
    decl_config: Union[DeclarativeConfig, None] = None,
) -> Callable[[T], T]:
    ...


def declarative(
    cls: Union[type, None] = None,
    /,
    *,
    config: Union[Config, None] = None,
    decl_config: Union[DeclarativeConfig, None] = None,
) -> Union[type, Callable]:
    def wrapper(cls: type) -> type:

        _config = config or getattr(cls, 'config', None) or _default_config
        _decl_config = (
            decl_config
            or getattr(cls, 'decl_config', None)
            or _default_decl_config
        )
        setattr(cls, '__init__', _make_init(cls, _config, _decl_config))
        type.__setattr__(cls, '__setattr__', _raise_type_error)
        type.__setattr__(cls, '__delattr__', _raise_type_error)
        return cls

    return wrapper if cls is None else wrapper(cls)


def _raise_type_error(*__args__, **__kwargs__):
    raise TypeError


def _make_init(cls: type, config: Config, decl_config: DeclarativeConfig):
    fields = _get_fieldtuples(cls)

    def __init__(self):
        for name, cast, default in fields:
            object.__setattr__(
                self,
                name,
                _resolve_value((name, cast, default), config, decl_config),
            )

    return __init__


def _get_fieldtuples(cls: type) -> tuple[FieldTuple]:
    annotations = {
        key: value
        for key, value in cls.__annotations__.items()
        if get_origin(value) is not ClassVar
        and not isinstance(cls.__dict__.get(key), (DeclarativeConfig, Config))
    }
    obj_defaults = {
        key: val for key, val in cls.__dict__.items() if key in annotations
    }
    return tuple(
        (key, _get_type(annotation), obj_defaults.get(key, MISSING))
        for key, annotation in annotations.items()
    )


def _get_type(annotation: type):
    if origin := get_origin(annotation):
        if origin is Union:
            return next(
                (item for item in get_args(annotation) if item is not None),
                origin,
            )
        if origin in (list, tuple, AbstractSequence, set):
            return _handle_list(origin, annotation)
    return annotation


def _handle_list(
    origin: type[Union[tuple, AbstractSequence, list, set]], annotation: type
):
    cast = typing.cast(
        type[Union[list, set, tuple]],
        tuple if origin is AbstractSequence else origin,
    )
    args = get_args(annotation)
    maxlen = slice(
        0, len(args) if origin is tuple and args[-1] is not Ellipsis else None,
    )
    return _wrap_list(cast, args[0], maxlen)


def _wrap_list(
    outercast: type[Union[list, set, tuple]], innercast: Any, maxlen: slice
):
    wrapper = comma_separated(innercast)

    def _wrap(value: Any):
        result = wrapper(value)[maxlen]
        return outercast(result)

    _wrap.__name__ = f'{innercast.__name__} sequence'
    return _wrap


def _resolve_value(
    fieldtuple: FieldTuple, config: Config, decl_config: DeclarativeConfig
):
    name, cast, default = fieldtuple
    field_name = _make_name(name, decl_config)
    try:
        return config(field_name, cast)
    except MissingName as e:
        val = _get_default(name, default, decl_config)
        if val is MISSING:
            raise e from None
        return val


def _make_name(name: str, decl_config: DeclarativeConfig) -> str:
    if name in decl_config.no_prefix or not decl_config.prefix:
        return decl_config.parser(name)
    return decl_config.parser('_'.join((decl_config.prefix, name)))


def _get_default(name: str, default: Any, decl_config: DeclarativeConfig):
    default = (
        default
        if default is not MISSING
        else decl_config.defaults.get(name, MISSING)
    )
    return default() if callable(default) else default
