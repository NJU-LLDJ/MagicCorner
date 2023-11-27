from pydantic import BaseModel


class User(BaseModel):
    uid: int

    @classmethod
    async def get_by_uid(cls, uid: int) -> "User":
        return cls(uid=uid)
