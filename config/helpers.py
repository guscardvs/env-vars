import typing
from collections.abc import Callable
from shlex import shlex

T = typing.TypeVar('T')


def comma_separated(
    cast: Callable[[str], T] = str
) -> typing.Callable[[str], tuple[T, ...]]:
    def _wrapped(val: str) -> tuple[T, ...]:
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
