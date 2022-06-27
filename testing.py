from contextlib import contextmanager
import typing
import copy

@contextmanager
def reset_mapping(mapping: typing.MutableMapping):
    copied = copy.deepcopy(mapping)
    yield mapping
    mapping.update(copied)
