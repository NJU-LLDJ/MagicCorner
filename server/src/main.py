from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import api
from db import MySQL, BaseDBConfig
from res import RuntimeResources
from server import Server, ServerConfig

res = RuntimeResources(
    Server(ServerConfig.from_file("server/config/server.json")),
    MySQL(BaseDBConfig.from_file("server/config/db.json")),
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
    # res.server.run(reload=True)
    import db.types

    print(db.types.INT.__name__)
