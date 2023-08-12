from enum import Enum
from typing import NamedTuple

from typing_extensions import Self


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
    LOCAL = EnvTuple("local", 1)
    TEST = EnvTuple("test", 2)
    DEV = EnvTuple("dev", 3)
    QA = EnvTuple("qa", 4)
    PRD = EnvTuple("prd", 5)

    @property
    def value(self) -> EnvTuple:
        """
        Get the value associated with the environment.
        
        Returns:
            EnvTuple: The value associated with the environment.
        """
        return super().value

    @property
    def val(self):
        """
        Get the environment value.
        
        Returns:
            str: The environment value.
        """
        return self.value.val

    @property
    def weight(self):
        """
        Get the weight associated with the environment.
        
        Returns:
            int: The weight associated with the environment.
        """
        return self.value.weight

    @classmethod
    def new(cls, val: str) -> Self:
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
            return next(value for value in cls if value.val == val)
        except StopIteration:
            raise ValueError(
                f"{val!r} is not a valid {cls.__name__}"
            ) from None
