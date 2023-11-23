import uvicorn

from utils.config import BaseConfig
from utils.singleton import singleton


class ServerConfig(BaseConfig):
    host: str
    port: int


@singleton
class Server:
    def __init__(self, config: ServerConfig):
        self.config = config

    def run(self, **kwargs):
        uvicorn.run("main:app", **self.config.model_dump(), **kwargs)
