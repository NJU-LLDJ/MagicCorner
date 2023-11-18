from fastapi import APIRouter
from pydantic import BaseModel

user = APIRouter()


class User(BaseModel):
    uid: int

    @classmethod
    async def get_by_uid(cls, uid: int) -> 'User':
        return cls(uid=uid)


@user.get("/me/")
async def get_me() -> dict[str, str]:
    return {"user": "me"}


@user.get("/{uid}/")
async def get_user(uid: int) -> User:
    return await User.get_by_uid(uid)
