import os
import string
import typing

from .exceptions import AlreadySet


class EnvMapping(typing.MutableMapping):
    def __init__(self, environ: typing.MutableMapping = os.environ):
        self._environ = environ
        self._has_been_read: typing.Set[typing.Any] = set()

    def __getitem__(self, key: typing.Any) -> typing.Any:
        self._has_been_read.add(key)
        return self._environ.__getitem__(key)

    def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
        if key in self._has_been_read:
            raise AlreadySet(
                f"Cannot set environ['{key}'], value has already been " 'read.'
            )
        self._environ.__setitem__(key, value)

    def __delitem__(self, key: typing.Any) -> None:
        if key in self._has_been_read:
            raise AlreadySet(
                f"Cannot delete environ['{key}'], value has already "
                'been read.'
            )
        self._environ.__delitem__(key)

    def __iter__(self) -> typing.Iterator:
        return iter(self._environ)

    def __len__(self) -> int:
        return len(self._environ)


class LowerEnvMapping(EnvMapping):
    def __init__(self, environ: typing.MutableMapping = os.environ):
        super().__init__(environ)
        self._environ = {
            key.lower(): value
            for key, value in self._environ.items()
            if all(map(lambda item: item in string.ascii_letters, key))
        }
