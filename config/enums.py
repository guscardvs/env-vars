from enum import Enum
from typing import Any, NamedTuple


class EnvTuple(NamedTuple):
    """
    A named tuple to represent environment values with associated weights.

    Attributes:
        val (str): The environment value.
        weight (int): The weight assigned to the environment value.
    """

    val: str
    weight: int


class Env(EnvTuple, Enum):
    """
    An enumeration representing different environment values with associated weights.

    Attributes:
        LOCAL (Env): The local environment.
        TEST (Env): The test environment.
        DEV (Env): The development environment.
        QA (Env): The quality assurance environment.
        PRD (Env): The production environment.
    """

    LOCAL = "local", 1
    TEST = "test", 2
    DEV = "dev", 3
    QA = "qa", 4
    PRD = "prd", 5
    ALWAYS = "always", 99

    @property
    def value(self) -> EnvTuple:
        """
        Get the value associated with the environment.

        Returns:
            EnvTuple: The value associated with the environment.
        """
        return super().value

    @property
    def name(self):
        """
        Get the environment value.

        Returns:
            str: The environment value.
        """
        return self.value.val

    @property
    def ordering(self):
        """
        Get the weight associated with the environment.

        Returns:
            int: The weight associated with the environment.
        """
        return self.value.weight

    @classmethod
    def _missing_(cls, value: object) -> Any:
        """
        Create a new instance of the Env enum based on the given environment value.

        Args:
            val (str): The environment value to create an instance for.

        Returns:
            Env: An instance of the Env enum based on the given value.

        Raises:
            ValueError: If the provided value is not a valid environment value.
        """
        try:
            return next(item for item in cls if item.name == value)
        except StopIteration:
            raise ValueError(f"{value!r} is not a valid {cls.__name__}") from None
