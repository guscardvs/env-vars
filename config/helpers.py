import typing
from collections.abc import Callable
from shlex import shlex

from ._helpers import as_callable

T = typing.TypeVar('T')


@typing.overload
def comma_separated(
    cast: Callable[[str], str] = as_callable(str)
) -> typing.Callable[[str], tuple[str, ...]]:
    ...


@typing.overload
def comma_separated(
    cast: Callable[[str], T]
) -> typing.Callable[[str], tuple[T, ...]]:
    ...


def comma_separated(
    cast: Callable[[str], T | str] = as_callable(str)
) -> typing.Callable[[str], tuple[T | str, ...]]:
    def _wrapped(val: str) -> tuple[T | str, ...]:
        lex = shlex(val, posix=True)
        lex.whitespace = ','
        lex.whitespace_split = True
        return tuple(cast(item.strip()) for item in lex)

    return _wrapped


_boolean_vals = {
    'true': True,
    'false': False,
    '0': False,
    '1': True,
}


def boolean(val: str | None) -> bool:
    if not val:
        return False
    try:
        return _boolean_vals[val.lower()]
    except KeyError as err:
        raise ValueError(
            f'Received invalid bool: {val}, try: {",".join(_boolean_vals)}'
        ) from err
