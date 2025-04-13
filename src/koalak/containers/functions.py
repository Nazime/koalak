import itertools
from typing import Any, Iterable

from .generic_container import Container, ContainerKey, DictContainer, T


def _get_appropriate_container(iterable) -> Container:
    # Checking the type of iterable to avoid consuming elements if it's a generator
    if isinstance(iterable, (list, tuple)):
        first_item = iterable[0]
    else:
        temp_iterator = iter(iterable)
        first_item = next(temp_iterator)
        iterable = itertools.chain([first_item], temp_iterator)

    if isinstance(first_item, dict):
        container = DictContainer
    else:
        container = Container
    return container(iterable, copy=False)


def first(iterable: Iterable[T], *args, **kwargs) -> T:
    container = _get_appropriate_container(iterable)
    return container.first(*args, **kwargs)


def search(iterable: Iterable[T], *args, key=None, **kwargs):
    if key:
        container = Container(iterable)
        container.get = key
    else:
        container = _get_appropriate_container(iterable)
    return container.search(*args, **kwargs)


def min(iterable: Iterable[T], *args, **kwargs) -> T:
    container = _get_appropriate_container(iterable)
    return container.min(*args, **kwargs)


def max(iterable: Iterable[T], *args, **kwargs) -> T:
    container = _get_appropriate_container(iterable)
    return container.max(*args, **kwargs)


def sum(iterable: Iterable[T], *args, **kwargs) -> Any:
    container = _get_appropriate_container(iterable)
    return container.sum(*args, **kwargs)


def count(iterable: Iterable[T], *args, **kwargs) -> int:
    container = _get_appropriate_container(iterable)
    return container.count(*args, **kwargs)


def count_values(iterable: Iterable[T], *args, **kwargs) -> int:
    container = _get_appropriate_container(iterable)
    return container.count_values(*args, **kwargs)
