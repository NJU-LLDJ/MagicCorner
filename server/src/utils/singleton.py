import functools
from typing import Generic, TypeVar

_T_co = TypeVar("_T_co", bound=object, covariant=True)


class Singleton(Generic[_T_co]):
    """
    Singleton class, use it as a decorator

    Example:
    ```
    @Singleton
    class A:
        pass
    ```
    """

    __slots__ = ("_cls", "_instance")

    def __init__(self, cls: type[_T_co]):
        self._cls = cls
        self._instance: object | None = None
        functools.wraps(self.__call__)(cls.__init__)

    def __call__(self, *args, **kwargs) -> _T_co:
        if self._instance is None:
            self._instance = self._cls(*args, **kwargs)
        return self._instance

    @property
    def instance(self) -> _T_co:
        return self._instance


def singleton(cls: type[_T_co]) -> Singleton[_T_co]:
    """Singleton decorator, alias of class Singleton"""

    return Singleton(cls)


class SingletonMeta(type):
    """
    Singleton metaclass, use it as a metaclass

    Example:
    ```
    class A(metaclass=SingletonMeta):
        pass
    ```
    """

    _instance: _T_co | None = None

    __slots__ = ()

    def __call__(cls: type[_T_co], *args, **kwargs) -> _T_co:
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

    @property
    def instance(cls) -> _T_co | None:
        if cls._instance is None:
            raise RuntimeWarning("Singleton instance is not initialized")
        return cls._instance
