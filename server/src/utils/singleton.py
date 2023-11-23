from typing import Generic, TypeVar

_T_co = TypeVar("_T_co", bound=object, covariant=True)


class Singleton(Generic[_T_co]):
    """Singleton class, use it as a decorator"""

    __slots__ = ("_cls", "_instance")

    def __init__(self, cls: type[_T_co]):
        self._cls = cls
        self._instance: object | None = None

    def __call__(self, *args, **kwargs) -> _T_co:
        if self._instance is None:
            self._instance = self._cls(*args, **kwargs)
        return self._instance


def singleton(cls: type[_T_co]) -> Singleton[_T_co]:
    """Singleton decorator, use it as a decorator"""

    return Singleton(cls)


class SingletonMeta(type):
    """Singleton metaclass, use it as a metaclass"""

    __slots__ = ()

    def __call__(cls: type[_T_co], *args, **kwargs) -> _T_co:
        if not hasattr(cls, "_instance"):
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance
