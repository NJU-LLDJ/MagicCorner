from db import *
from model.v1.crud import CRUD


class User(CRUD):
    uid: int

    @classmethod
    def table_name(cls) -> str:
        return cls.__name__

    @classmethod
    def table_columns(cls) -> dict[str, MySQLDataType]:
        return {"uid": INT(primary_key=True)}

    @classmethod
    async def get_by_uid(cls, uid: int) -> "User":
        return cls(uid=uid)
