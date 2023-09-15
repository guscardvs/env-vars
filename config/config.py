import os
from os import environ
from pathlib import Path
from typing import (
    Any,
    Callable,
    Iterator,
    MutableMapping,
    TypeVar,
    Union,
    overload,
)

from gyver.attrs import define, info

from config._helpers import clean_dotenv_value, panic
from lazyfields import lazyfield
from config.exceptions import InvalidCast, InvalidEnv, MissingName
from config.interface import MISSING, _default_cast

T = TypeVar("T")


@define
class EnvMapping(MutableMapping[str, str]):
    """
    A mutable mapping representing the environment variables.
    """

    mapping: MutableMapping[str, str] = environ
    already_read: set[str] = info(default_factory=set)

    def __getitem__(self, name: str):
        """
        Get the value of the specified environment variable.

        Args:
            name (str): The name of the environment variable.

        Returns:
            str: The value of the environment variable.

        Raises:
            KeyError: If the environment variable is not found.
        """
        val = self.mapping[name]
        self.already_read.add(name)
        return val

    def __setitem__(self, name: str, value: str):
        """
        Set the value of the specified environment variable.

        Args:
            name (str): The name of the environment variable.
            value (str): The new value for the environment variable.

        Raises:
            KeyError: If the environment variable has already been read.
        """
        if name in self.already_read:
            raise panic(
                KeyError, f"{name} already read, cannot change its value"
            )
        self.mapping[name] = value

    def __delitem__(self, name: str) -> None:
        """
        Delete the specified environment variable.

        Args:
            name (str): The name of the environment variable.

        Raises:
            KeyError: If the environment variable has already been read.
        """
        if name in self.already_read:
            raise panic(KeyError, f"{name} already read, cannot delete")
        del self.mapping[name]

    def __iter__(self) -> Iterator[str]:
        """
        Iterate through the environment variable names.

        Yields:
            str: The names of environment variables.
        """
        yield from self.mapping

    def __len__(self) -> int:
        """
        Get the number of environment variables.

        Returns:
            int: The number of environment variables.
        """
        return len(self.mapping)


default_mapping = EnvMapping()


@define
class Config:
    """
    Configuration settings for working with environment variables.
    """

    env_file: Union[str, Path, None] = None
    mapping: EnvMapping = default_mapping

    def __post_init__(self):
        """
        Initialize the Config instance after construction.

        Reads values from the environment file and updates the internal mapping if necessary.
        """
        if self.env_file and os.path.isfile(self.env_file):
            self.file_values.update(dict(self._read_file(self.env_file)))

    @lazyfield
    def file_values(self):
        """
        Lazy field for storing values read from the environment file.

        Returns:
            dict: Dictionary containing values read from the environment file.
        """
        return {}

    def _read_file(self, env_file: Union[str, Path]):
        """
        Read values from the environment file.

        Args:
            env_file (Union[str, Path]): The path to the environment file.

        Yields:
            tuple[str, str]: Pairs of environment variable names and their values.
        """
        with open(env_file, "r") as buf:
            for line in buf:
                line = (
                    line.strip()
                )  # Remove leading/trailing whitespaces and newlines
                if not line or line.startswith(
                    "#"
                ):  # Skip empty lines and full-line comments
                    continue

                # Handle lines with comments after the value

                name, value = line.split("=", 1)
                if " #" in value:
                    value, comment = value.strip().split(" #", 1)
                    maybe_quote = value[0]
                    if (
                        maybe_quote in "'\""
                        and value[-1] != maybe_quote
                        and comment[-1] == maybe_quote
                    ):
                        value = f"{value} #{comment}"

                yield name.strip(), clean_dotenv_value(value)

    def _cast(self, name: str, val: Any, cast: Callable) -> Any:
        """
        Cast a value to the specified type using a casting function.

        Args:
            name (str): The name of the environment variable.
            val (Any): The value to be cast.
            cast (Callable): The casting function.

        Returns:
            Any: The casted value.

        Raises:
            InvalidCast: If casting the value is unsuccessful.
        """
        try:
            val = cast(val)
        except Exception as e:
            raise panic(
                InvalidCast, f"{name} received an invalid value {val}"
            ) from e
        else:
            return val

    def _get_val(
        self, name: str, default: Union[Any, type[MISSING]] = MISSING
    ) -> Union[Any, type[MISSING]]:
        """
        Get the value of the specified environment variable.

        Args:
            name (str): The name of the environment variable.
            default (Union[Any, type[MISSING]], optional):
                The default value to return if the variable is not found. Defaults to MISSING.

        Returns:
            Union[Any, type[MISSING]]: The value of the environment variable if found, or the default value.

        Raises:
            MissingName: If the environment variable is not found and no default value is provided.
        """
        return self.mapping.get(name, self.file_values.get(name, default))

    def get(
        self,
        name: str,
        cast: Callable = _default_cast,
        default: Union[Any, type[MISSING]] = MISSING,
    ) -> Any:
        """
        Get the value of the specified environment variable, optionally casting it.

        Args:
            name (str): The name of the environment variable.
            cast (Callable, optional): The casting function. Defaults to _default_cast.
            default (Union[Any, type[MISSING]], optional):
                The default value to return if the variable is not found. Defaults to MISSING.

        Returns:
            Any: The value of the environment variable, casted if necessary.

        Raises:
            MissingName: If the environment variable is not found and no default value is provided.
            InvalidCast: If casting the value is unsuccessful.
        """
        val = self._get_val(name, default)
        if val is MISSING:
            raise panic(
                MissingName, f"{name} not found and no default was given"
            )
        return self._cast(name, val, cast)

    @overload
    def __call__(
        self,
        name: str,
        cast: Union[Callable[[Any], T], type[T]] = _default_cast,
        default: type[MISSING] = MISSING,
    ) -> T:
        ...

    @overload
    def __call__(
        self,
        name: str,
        cast: Union[Callable[[Any], T], type[T]] = _default_cast,
        default: T = ...,
    ) -> T:
        ...

    def __call__(
        self,
        name: str,
        cast: Union[Callable[[Any], T], type[T]] = _default_cast,
        default: Union[T, type[MISSING]] = MISSING,
    ) -> T:
        """
        Get the value of the specified environment variable, optionally casting it using the callable syntax.

        Args:
            name (str): The name of the environment variable.
            cast (Union[Callable[[Any], T], type[T]], optional):
                The casting function or type. Defaults to _default_cast.
            default (Union[T, type[MISSING]], optional):
                The default value to return if the variable is not found. Defaults to MISSING.

        Returns:
            T: The value of the environment variable, casted if necessary.

        Raises:
            MissingName: If the environment variable is not found and no default value is provided.
            InvalidCast: If casting the value is unsuccessful.
        """
        return self.get(name, cast, default)
