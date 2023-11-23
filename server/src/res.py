from database import MySQL
from server import Server
from utils.singleton import singleton


@singleton
class RuntimeResources:
    def __init__(self, server: Server, db: MySQL):
        self.server: Server = server
        self.db: MySQL = db
