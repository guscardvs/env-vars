import contextlib
import typing
from collections.abc import Callable

from config.exceptions import StrictCast

T = typing.TypeVar("T")
P = typing.ParamSpec("P")

ExcT = typing.TypeVar("ExcT", bound=Exception)


def panic(exc: type[ExcT], message: str, *excargs) -> ExcT:
    return exc(f"{message.removesuffix('!')}!", *excargs)


def clean_dotenv_value(value: str) -> str:
    """clean_dotenv_value removes leading and trailing whitespace and removes
    wrapping quotes from the value."""
    # Remove leading and trailing whitespace
    value = value.strip()

    # Check if value has quotes at the beginning and end
    has_quotes = len(value) >= 2 and value[0] == value[-1] and value[0] in ['"', "'"]

    # Remove quotes if they exist (only once)
    if has_quotes:
        value = value[1:-1]

    return value


class maybe_result(typing.Generic[P, T]):
    """Raises error if receives None value on .strict()"""

    def __init__(
        self,
        func: Callable[P, T | None],
    ):
        self._func = func

    def strict(self, *args: P.args, **kwargs: P.kwargs) -> T:
        if (result := self._func(*args, **kwargs)) is not None:
            return result
        raise panic(StrictCast, f"received falsy value {result}", result)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T | None:
        return self._func(*args, **kwargs)

    def optional(self, *args: P.args, **kwargs: P.kwargs) -> T | None:
        with contextlib.suppress(Exception):
            return self._func(*args, **kwargs)


def closing_quote_position(value: str) -> int | None:
    """Returns the position of the closing quote."""
    quotes = ("'", '"')
    if value[0] not in quotes:
        # string does not start with a quote
        return None
    quote_char = value[0]
    closing_quote = next(
        (
            position
            for position, token in enumerate(value[1:], 1)
            if token == quote_char and value[position - 1] != "\\"
        ),
        None,
    )
    return closing_quote


def strip_comment(value: str, closing_quote: int | None = None) -> str:
    """
    Remove comments from the string. A comment starts with a '#'
    character preceded by a space or a tab.

    Args:
        value (str): The input string which might contain a comment.
        closing_quote (int | None): Position of the closing quote, if any.
    Returns:
        str: The string without the comment.
    """

    if "#" not in value:
        return value
    closing_quote = closing_quote or 0
    if closing_quote == len(value) - 1:
        # String is fully quoted
        return value
    comment_starts = next(
        (
            position
            for position, token in enumerate(value[closing_quote:], closing_quote)
            if token == "#" and position != 0 and value[position - 1] in (" ", "\t")
        ),
        None,
    )
    if comment_starts is None:
        return value
    return value[:comment_starts].rstrip()
