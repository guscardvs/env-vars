from enum import Enum
from typing import NamedTuple

from typing_extensions import Self


class EnvTuple(NamedTuple):
    val: str
    weight: int


class Env(EnvTuple, Enum):
    LOCAL = EnvTuple("local", 1)
    TEST = EnvTuple("test", 2)
    DEV = EnvTuple("dev", 3)
    QA = EnvTuple("qa", 4)
    PRD = EnvTuple("prd", 5)

    @property
    def value(self) -> EnvTuple:
        return super().value

    @property
    def val(self):
        return self.value.val

    @property
    def weight(self):
        return self.value.weight

    @classmethod
    def new(cls, val: str) -> Self:
        try:
            return next(value for value in cls if value.val == val)
        except StopIteration:
            raise ValueError(
                f"{val!r} is not a valid {cls.__name__}"
            ) from None
