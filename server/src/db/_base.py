from abc import ABC, abstractmethod
from collections.abc import MutableMapping, Callable
from functools import wraps
from typing import TypeVar, ParamSpec

import aiomysql  # type: ignore
import pymysql

from utils.config import BaseConfig

_DB = TypeVar("_DB", bound="BaseDB", covariant=True)
_T = TypeVar("_T")
_P = ParamSpec("_P")


class BaseDBConfig(BaseConfig):
    host: str
    port: int
    user: str
    password: str
    autocommit: bool = True


class BaseDB(MutableMapping[str, _DB], ABC):
    __slots__ = ("_data", "_config", "_name", "_sync_conn", "_async_pool", "_is_root")

    def __init__(
        self,
        config: BaseDBConfig,
        name: str,
        sync_conn: pymysql.Connection | None,
        async_pool: aiomysql.Pool | None,
        is_root: bool,
    ):
        super().__init__()
        self._data: dict[str, _DB] = {}
        self._config = config
        self._name = name
        self._sync_conn: pymysql.Connection | None = sync_conn
        self._async_pool: aiomysql.Pool | None = async_pool
        self._is_root = is_root

    @property
    def config(self) -> BaseConfig:
        return self._config

    @property
    def name(self) -> str:
        return self._name

    def connect(self, **kwargs):
        """同步连接数据库"""
        if self._is_root and self._sync_conn is None:
            kwargs.update(self._config.model_dump())
            if "autocommit" not in kwargs:
                kwargs.update(autocommit=True)
            self._sync_conn = pymysql.connect(**kwargs)

    async def connect_async(self, **kwargs):
        """异步连接数据库"""
        if self._is_root and self._async_pool is None:
            kwargs.update(self._config.model_dump())
            if "autocommit" not in kwargs:
                kwargs.update(autocommit=True)
            self._async_pool = await aiomysql.create_pool(**kwargs)

    def __del__(self):
        if self._is_root:
            # 没有self.terminate_async()，因为在__del__中不能使用await
            self.terminate()

    def close(self):
        """关闭同步数据库连接"""
        if self._is_root and self._sync_conn is not None:
            self._sync_conn.close()

    async def close_async(self):
        """关闭异步数据库连接"""
        if self._is_root and self._async_pool is not None:
            self._async_pool.close()
            await self._async_pool.wait_closed()

    terminate = close
    terminate.__doc__ = "终止同步数据库连接"

    async def terminate_async(self):
        """终止异步数据库连接"""
        print("terminate_async")
        if self._is_root and self._async_pool is not None:
            self._async_pool.terminate()
            await self._async_pool.wait_closed()

    def execute(self, query: str, *args) -> tuple:
        with self._sync_conn.cursor() as cur:
            cur.execute(query, args)
            return cur.fetchall()

    def executemany(self, query: str, args: list[tuple]) -> tuple:
        with self._sync_conn.cursor() as cur:
            cur.executemany(query, args)
            return cur.fetchall()

    async def execute_async(self, query: str, *args) -> tuple:
        async with self._async_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                return await cur.fetchall()

    async def executemany_async(self, query: str, args: list[tuple]) -> tuple:
        async with self._async_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.executemany(query, args)
                return await cur.fetchall()

    @abstractmethod
    def _create_value(self, *args, **kwargs) -> _DB:
        pass


def _sync_opr(func: Callable[_P, _T]) -> Callable[_P, _T]:
    @wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs):
        args[0].connect()
        return func(*args, **kwargs)

    return wrapper


def _async_opr(func: Callable[_P, _T]) -> Callable[_P, _T]:
    @wraps(func)
    async def wrapper(*args: _P.args, **kwargs: _P.kwargs):
        await args[0].connect_async()
        return await func(*args, **kwargs)

    return wrapper
