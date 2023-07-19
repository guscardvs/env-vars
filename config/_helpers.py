import contextlib
import typing

from typing_extensions import ParamSpec, Self

from config.exceptions import StrictCast

T = typing.TypeVar("T")
SelfT = typing.TypeVar("SelfT")
P = ParamSpec("P")

_obj_setattr = object.__setattr__


class lazyfield(typing.Generic[SelfT, T]):
    """A descriptor class that can be used as a decorator for a method on a
    class.

    When the decorated method is accessed on an instance, it will check
    if the instance has an attribute with the same name as the method
    but with an underscore prefix. If the attribute does not exist, it
    will call the decorated method on the instance and set the result as
    the attribute's value. Subsequent accesses will return the cached
    value, avoiding unnecessary recalculation or computation.
    """

    def __init__(self, func: typing.Callable[[SelfT], T]) -> None:
        """
        func : callable
            The function that will be decorated. This function should take
            a single argument, which is the instance of the class it is a
            method of.
        """
        self._func = func

    def __set_name__(self, owner: type[SelfT], name: str):
        self.public_name = name
        self.private_name = f"_lazyfield_{name}"

    @typing.overload
    def __get__(self, instance: SelfT, owner: type[SelfT]) -> T:
        ...

    @typing.overload
    def __get__(
        self, instance: typing.Literal[None], owner: type[SelfT]
    ) -> Self:
        ...

    def __get__(
        self,
        instance: typing.Optional[SelfT],
        owner: typing.Optional[type[SelfT]] = None,
    ) -> typing.Union[T, Self]:
        if not instance:
            return self
        try:
            val = typing.cast(
                T,
                object.__getattribute__(
                    instance,
                    self.private_name,
                ),
            )
        except AttributeError:
            val = self._try_set(instance)
        return val

    def _try_set(self, instance: SelfT) -> T:
        try:
            val = self._func(instance)
        except Exception as e:
            # remove exception context to create easier traceback
            raise e from None
        else:
            _obj_setattr(instance, self.private_name, val)
            return val

    def __set__(self, instance: SelfT, value: T):
        self.manual_set(instance, value)

    def __delete__(self, instance: SelfT):
        self.cleanup(instance)

    def cleanup(self, instance: SelfT):
        object.__delattr__(instance, self.private_name)

    def manual_set(self, instance: SelfT, value: T):
        _obj_setattr(instance, self.private_name, value)


ExcT = typing.TypeVar("ExcT", bound=Exception)


def panic(exc: type[ExcT], message: str, *excargs) -> ExcT:
    raise exc(f"{message.removesuffix('!')}!", *excargs)


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
