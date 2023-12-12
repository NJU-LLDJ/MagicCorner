from collections.abc import Callable
from typing import TypeVar

_T = TypeVar("_T")


def iife(func: Callable[[], _T]) -> _T:
    """Immediately Invoked Function Expression"""
    return func()
