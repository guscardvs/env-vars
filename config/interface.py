from typing import Any, Protocol, TypeVar, overload
from collections.abc import Callable


class MISSING:
    pass


def _default_cast(a: Any):
    return a


T = TypeVar("T")


class ConfigLike(Protocol):
    def get(
        self,
        name: str,
        cast: Callable = _default_cast,
        default: Any | type[MISSING] = MISSING,
    ) -> Any: ...

    @overload
    def __call__(
        self,
        name: str,
        cast: Callable[[Any], T] | type[T] = _default_cast,
        default: type[MISSING] = MISSING,
    ) -> T: ...

    @overload
    def __call__(
        self,
        name: str,
        cast: Callable[[Any], T] | type[T] = _default_cast,
        default: T = ...,
    ) -> T: ...

    def __call__(
        self,
        name: str,
        cast: Callable[[Any], T] | type[T] = _default_cast,
        default: T | type[MISSING] = MISSING,
    ) -> T: ...
