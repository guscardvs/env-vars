from collections.abc import Callable
from typing import Any, Protocol, TypeVar, overload


class MISSING:
    pass


def default_cast(a: Any):
    return a


T = TypeVar("T")


class ConfigLike(Protocol):
    def get(
        self,
        name: str,
        cast: Callable = default_cast,
        default: Any | type[MISSING] = MISSING,
    ) -> Any: ...

    @overload
    def __call__(
        self,
        name: str,
        cast: Callable[[Any], T] | type[T] = default_cast,
        default: type[MISSING] = MISSING,
    ) -> T: ...

    @overload
    def __call__(
        self,
        name: str,
        cast: Callable[[Any], T] | type[T] = default_cast,
        default: T = ...,
    ) -> T: ...

    def __call__(
        self,
        name: str,
        cast: Callable[[Any], T] | type[T] = default_cast,
        default: T | type[MISSING] = MISSING,
    ) -> T: ...
