import warnings
from typing import Optional


class SingletonMeta(type):
    """
    Singleton metaclass, use it as a metaclass

    Example:
        >>> class A(metaclass=SingletonMeta):
        ...     def __init__(self, n: int):
        ...         self.n = n

        >>> a = A(1)
        >>> b = A(2)
        >>> a is b
        True
        >>> a.n == b.n == 1
        True
    """

    _instance: Optional[object] = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

    @property
    def instance(cls):
        if cls._instance is None:
            warnings.warn(f"Singleton Class {cls.__qualname__} is not initialized")
        return cls._instance


class Singleton(metaclass=SingletonMeta):
    """
    Singleton class, inherit it to make a singleton class

    Example:
        >>> class A(Singleton):
        ...     def __init__(self, n: int):
        ...         self.n = n

        >>> a = A(1)
        >>> b = A(2)
        >>> a is b
        True
        >>> a.n == b.n == 1
        True
    """


def singleton(cls: type):
    """
    Singleton decorator, use it as a decorator

    Issue:
        This decorator makes it hard for IDE to recognize the type of the decorated class.
        It is recommended to use the Singleton class or SingletonMeta metaclass instead.

    Example:
        >>> @singleton
        ... class A:
        ...     def __init__(self, n: int):
        ...         self.n = n

        >>> a = A(1)
        >>> b = A(2)
        >>> a is b
        True
        >>> a.n == b.n == 1
        True
    """

    class SingletonWrapper(cls, metaclass=SingletonMeta):
        pass

    return SingletonWrapper
