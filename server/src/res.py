from database import MySQL
from utils.singleton import singleton


@singleton
class RuntimeResources:
    def __init__(self, db: MySQL):
        self.db: MySQL = db
