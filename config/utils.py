from collections.abc import Callable
from pathlib import Path
from shlex import shlex
from typing import Any, Generic, Literal, NamedTuple, TypeVar, Union, overload

from config._helpers import maybe_result
from config.exceptions import InvalidCast, InvalidEnv


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
    cast: Callable[[str], str] = str,
) -> Callable[[str], tuple[str, ...]]: ...


@overload
def comma_separated(cast: Callable[[str], T]) -> Callable[[str], tuple[T, ...]]: ...


def comma_separated(
    cast: Callable[[str], Union[T, str]] = str,
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


LiteralType = type(Literal["Any"])


class ArgTuple(NamedTuple):
    arg: str
    cast: type


def literal_cast(literal_decl: Any):
    """
    Converts a value to one of the literals defined in the provided literal declaration.

    Args:
        literal_decl (Any): The literal declaration, typically a `Literal` type annotation.

    Returns:
        Callable[[str], Any]: A casting function that checks if the value matches any of the literals defined
            in the declaration. If a match is found, it returns the value as is. Otherwise, it raises an `InvalidCast`
            exception.

    Raises:
        TypeError: If the provided literal declaration is not an instance of `Literal`.
        InvalidCast: If the value received does not match any argument from the literal declaration.

    Examples:
        >>> literal_cast(Literal["Any"])("Any")
        'Any'
        >>> literal_cast(Literal[1, "two", 3.0])("3.0")
        3.0
        >>> literal_cast(Literal[1, "two", 3.0])("four")
        Traceback (most recent call last):
            ...
        InvalidCast: Value received does not match any argument from literal: (1, 'two', 3.0)
    """
    if not isinstance(literal_decl, LiteralType):
        raise TypeError
    arg_map = tuple(ArgTuple(arg, type(arg)) for arg in literal_decl.__args__)

    def _cast(val: str) -> Any:
        for arg, cast in arg_map:
            if cast(val) == arg:
                return val
        else:
            raise InvalidCast(
                "Value received does not match any argument from literal",
                literal_decl.__args__,
            )

    return _cast
