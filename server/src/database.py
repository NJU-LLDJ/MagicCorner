import asyncio
import aiomysql

from utils.config import BaseConfig
from utils.singleton import singleton


class MySQLConfig(BaseConfig):
    host: str
    port: int
    user: str
    password: str
    db: str


@singleton
class MySQL:
    def __init__(
        self,
        config: MySQLConfig,
        loop: asyncio.AbstractEventLoop | None = None,
    ):
        self._config: MySQLConfig = config
        self._loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        self._pool: aiomysql.pool.Pool | None = None

    def __del__(self):
        if self._pool is not None and not self._pool.closed:
            self._loop.run_until_complete(self.terminate())

    @property
    def config(self) -> MySQLConfig:
        return self._config

    @config.setter
    def config(self, config: MySQLConfig):
        self._config = config

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @property
    def pool(self) -> aiomysql.pool.Pool:
        if self._pool is None:
            raise RuntimeError("MySQL pool is not initialized")
        return self._pool

    async def connect(self, **kwargs):
        self._pool = await aiomysql.create_pool(
            loop=self._loop,
            **self._config.model_dump(),
            **kwargs,
        )

    async def close(self):
        self._pool.close()
        await self._pool.wait_closed()

    async def terminate(self):
        self._pool.terminate()
        await self._pool.wait_closed()

    async def execute(self, query: str, *args) -> list:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                return await cur.fetchall()

    async def executemany(self, query: str, args: list[tuple]) -> list:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.executemany(query, args)
                return await cur.fetchall()
