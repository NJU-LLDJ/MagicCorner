import json
from _typeshed import OpenBinaryModeReading, OpenTextModeReading, StrOrBytesPath
from types import ModuleType
from typing import Any, AnyStr, IO, Optional, ParamSpec, Protocol, Self, TypeVar

from pydantic import BaseModel

_D_co = TypeVar("_D_co", bound=dict[str, Any], covariant=True)
_P = ParamSpec("_P")


class SupportsLoad(Protocol[_P, _D_co]):
    """支持load方法的协议"""

    @staticmethod
    def load(file: IO[AnyStr], *args: _P.args, **kwargs: _P.kwargs) -> _D_co:
        """
        从文件中加载数据

        Args:
            file: 文件对象
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            数据对象，要求是dict[str, Any]的子类
        """
        pass


class BaseConfig(BaseModel):
    @classmethod
    def load(
        cls,
        path: StrOrBytesPath,
        mode: OpenTextModeReading | OpenBinaryModeReading = "r",
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        serializer: ModuleType | SupportsLoad[_P, _D_co] = json,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> Self:
        """
        从文件中加载配置

        Args:
            path: 文件路径
            mode: 打开文件的模式，只允许读取，默认为'r'
            encoding: 文件编码，默认为None
            errors: 编码错误处理，默认为None
            serializer: 序列化器，默认为json，或者是实现SupportsLoad协议的类
            *args: 传递给serializer.load的位置参数
            **kwargs: 传递给serializer.load的关键字参数

        Returns:
            配置对象
        """
        with open(path, mode, encoding=encoding, errors=errors) as file:
            d = serializer.load(file, *args, **kwargs)
        return cls(**d)
