class AlreadySet(Exception):
    pass


class MissingName(KeyError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Config '{name}' is missing, and has no default.")


class InvalidCast(ValueError):
    pass
