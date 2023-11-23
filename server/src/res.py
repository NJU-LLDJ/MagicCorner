from database import MySQL
from server import Server
from utils.singleton import SingletonMeta


class RuntimeResources(metaclass=SingletonMeta):
    def __init__(self, server: Server, db: MySQL):
        self.server: Server = server
        self.db: MySQL = db
