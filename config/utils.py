from shlex import shlex
from typing import Callable, TypeVar, Union, overload

from config._helpers import maybe_result


@maybe_result
def boolean_cast(string: str):
    """The boolean_cast function converts a string to its boolean equivalent. 1
    and true(case-insensitive) are considered True, everything else, False.

    :param string: str: Check if the string is true or false
    :return: A boolean value based on the string it receives
    """
    return {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "": False,
    }.get(string.lower())


val = boolean_cast("true")

T = TypeVar("T")


@overload
def comma_separated(
    cast: Callable[[str], str] = str
) -> Callable[[str], tuple[str, ...]]:
    ...


@overload
def comma_separated(
    cast: Callable[[str], T]
) -> Callable[[str], tuple[T, ...]]:
    ...


def comma_separated(
    cast: Callable[[str], Union[T, str]] = str
) -> Callable[[str], tuple[Union[T, str], ...]]:
    def _wrapped(val: str) -> tuple[Union[T, str], ...]:
        lex = shlex(val, posix=True)
        lex.whitespace = ","
        lex.whitespace_split = True
        return tuple(cast(item.strip()) for item in lex)

    return _wrapped
