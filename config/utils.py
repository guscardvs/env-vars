from pathlib import Path
from shlex import shlex
from typing import Any, Callable, Generic, TypeVar, Union, overload

from config._helpers import maybe_result
from config.exceptions import InvalidEnv


@maybe_result
def boolean_cast(string: str):
    """
    Converts a string to its boolean equivalent.

    1 and true (case-insensitive) are considered True, everything else is False.

    Args:
        string (str): The string to check if it represents a boolean value.

    Returns:
        MaybeResult[P, bool]: A maybe result helper. If called normally, it returns an Optional[bool].
        If called with `.strict(string)`, it raises an error if `boolean_cast` returns None.
        If called with `.optional(string)`, it returns Optional[bool], suppressing exceptions caused by None values.
    """
    return {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "": False,
    }.get(string.lower())


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
    """
    Converts a comma-separated string to a tuple of values after applying the given cast function.

    Args:
        cast (Callable[[str], Union[T, str]]): The casting function to apply to each item in the comma-separated string.
            Defaults to `str`.

    Returns:
        Callable[[str], tuple[Union[T, str], ...]]: A callable that returns a tuple containing the casted values
            from the comma-separated string.
    """

    def _wrapped(val: str) -> tuple[Union[T, str], ...]:
        lex = shlex(val, posix=True)
        lex.whitespace = ","
        lex.whitespace_split = True
        return tuple(cast(item.strip()) for item in lex)

    return _wrapped


T = TypeVar("T")


def valid_path(val: str) -> Path:
    """
    Converts a string to a Path object and checks if the path exists.

    Args:
        val (str): The string representing a file path.

    Raises:
        FileNotFoundError: If the path does not exist.

    Returns:
        Path: A Path object representing the file path.
    """
    valpath = Path(val)
    if not valpath.exists():
        raise FileNotFoundError(f"Path {valpath!s} is not valid path", valpath)
    return valpath


S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")


class _JoinedCast(Generic[S, T]):
    """
    A utility class for chaining casting operations.
    """
    def __init__(self, cast: Callable[[S], T]) -> None:
        self._cast = cast

    def __call__(self, val: S) -> T:
        return self._cast(val)

    def cast(self, cast: Callable[[T], U]) -> "_JoinedCast[S, U]":
        """
        Chain a new casting operation to the existing `_JoinedCast` instance.

        Args:
            cast (Callable[[T], U]): The casting function to apply.

        Returns:
            _JoinedCast[S, U]: A new `_JoinedCast` instance that applies the chained casting operation.
        """
        return _JoinedCast(self._make_cast(cast))

    def _make_cast(self, cast: Callable):
        """
        Create a new casting operation based on the existing `_JoinedCast` instance.

        Args:
            cast (Callable): The casting function to apply.

        Returns:
            Callable: A new casting function that combines the existing casting function and the provided one.
        """
        def _wrapper(val: Any):
            return cast(self._cast(val))

        return _wrapper


def joined_cast(cast: Callable[[str], T]) -> _JoinedCast[str, T]:
    """
    Creates a joined casting function for chaining casting operations.

    Args:
        cast (Callable[[str], T]): The casting function to apply.

    Returns:
        _JoinedCast[str, T]: A `_JoinedCast` object that allows chaining casting operations.
    """
    return _JoinedCast(cast)


def with_rule(rule: Callable[[Any], bool]):
    """
    Applies a rule check on a value, raising an `InvalidEnv` exception if the rule is not satisfied.

    Args:
        rule (Callable[[Any], bool]): The rule function to apply.

    Raises:
        InvalidEnv: If the rule condition is not met.

    Returns:
        Callable[[T], T]: A caster function that applies the rule check.
    """

    def caster(val: T) -> T:
        if not rule(val):
            raise InvalidEnv(
                f"Value {val} did not pass rule check {rule.__name__}",
                rule,
                val,
            )
        return val

    return caster
