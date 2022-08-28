import typing
from functools import cache

T = typing.TypeVar('T')
P = typing.ParamSpec('P', bound=typing.Hashable)  # type: ignore


def memoize(func: typing.Callable[P, T]) -> typing.Callable[P, T]:
    return typing.cast(typing.Callable[P, T], cache(func))


@memoize
def as_callable(typ: type[T]) -> typing.Callable[[str], T]:
    """simple wrapper to types to make mypy happy
    use as cast=as_callable(str)"""

    def converter(val: str) -> T:
        return typ(val)  # type: ignore

    return converter
