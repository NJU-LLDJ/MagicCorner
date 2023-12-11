import json
from _typeshed import OpenTextMode
from os import PathLike
from types import ModuleType
from typing import IO, Protocol, runtime_checkable, TypeVar, Any

from pydantic import BaseModel

_L_co = TypeVar("_L_co", bound=dict, covariant=True)


@runtime_checkable
class SupportsLoad(Protocol[_L_co]):
    @staticmethod
    def load(buffer: IO) -> _L_co:
        raise NotImplementedError


class BaseConfig(BaseModel):
    @classmethod
    def load(
        cls,
        path: str | bytes | PathLike[str] | PathLike[bytes],
        mode: OpenTextMode = "r",
        encoding: str | None = None,
        serialize_module: SupportsLoad[dict[str, Any]] | ModuleType = json,
    ) -> "BaseConfig":
        with open(path, mode, encoding=encoding) as file:
            d = serialize_module.load(file)
        return cls(**d)
