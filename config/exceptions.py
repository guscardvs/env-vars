class ConfigError(Exception):
    """Base Exception for all errors in package"""


class AlreadySet(ConfigError):
    pass


class MissingName(ConfigError, KeyError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Config '{name}' is missing, and has no default.")


class InvalidCast(ConfigError, ValueError):
    pass
