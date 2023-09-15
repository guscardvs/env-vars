import contextlib
import typing

from typing_extensions import ParamSpec, Self

from config.exceptions import StrictCast

T = typing.TypeVar("T")
P = ParamSpec("P")

ExcT = typing.TypeVar("ExcT", bound=Exception)


def panic(exc: type[ExcT], message: str, *excargs) -> ExcT:
    return exc(f"{message.removesuffix('!')}!", *excargs)


def clean_dotenv_value(value: str) -> str:
    """clean_dotenv_value removes leading and trailing whitespace and removes
    wrapping quotes from the value."""
    # Remove leading and trailing whitespace
    value = value.strip()

    # Check if value has quotes at the beginning and end
    has_quotes = (
        len(value) >= 2 and value[0] == value[-1] and value[0] in ['"', "'"]
    )

    # Remove quotes if they exist (only once)
    if has_quotes:
        value = value[1:-1]

    return value


class maybe_result(typing.Generic[P, T]):
    """Raises error if receives None value on .strict()"""

    def __init__(
        self,
        func: typing.Callable[P, typing.Optional[T]],
    ):
        self._func = func

    def strict(self, *args: P.args, **kwargs: P.kwargs) -> T:
        if (result := self._func(*args, **kwargs)) is not None:
            return result
        raise panic(StrictCast, f"received falsy value {result}", result)

    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> typing.Optional[T]:
        return self._func(*args, **kwargs)

    def optional(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> typing.Optional[T]:
        with contextlib.suppress(Exception):
            return self._func(*args, **kwargs)
