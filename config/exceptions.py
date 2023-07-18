class ConfigError(Exception):
    """Base Exception for all env-star errors."""


class InvalidCast(ConfigError):
    """Exception raised for config when cast callable raises an error."""


class MissingName(ConfigError, KeyError):
    """Exception raised for config when name is not found in given environ."""


class AlreadySet(ConfigError):
    """Exception raised for config when a value is already set."""


class StrictCast(InvalidCast):
    """Exception raised when strict is used for cast."""
