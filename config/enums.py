from enum import Enum


class Env(Enum):
    LOCAL = 'local'
    DEV = 'dev'
    TEST = 'test'
    PRD = 'prd'

    @classmethod
    def iter(cls):
        for item in cls:
            yield item.value
