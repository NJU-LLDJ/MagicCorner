from contextlib import asynccontextmanager
from fastapi import FastAPI

from api import api
from res import RuntimeResources
from database import MySQL, MySQLConfig

res = RuntimeResources(
    MySQL(MySQLConfig.from_file("server/config/db.json")),
)


# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(a: FastAPI) -> None:
    await res.db.connect()
    yield
    await res.db.close()


# noinspection PyTypeChecker
app = FastAPI(lifespan=lifespan)
app.include_router(api, prefix="/api", tags=["api"])


@app.get("/")
async def root() -> str:
    return "Hello World"


if __name__ == "__main__":
    from server import ServerConfig, Server

    server = Server(ServerConfig.from_file("server/config/server.json"))
    server.run()
