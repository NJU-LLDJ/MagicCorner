from fastapi import APIRouter

from model.v1.user import User

user = APIRouter()


@user.get("/me/")
async def get_me() -> dict[str, str]:
    return {"user": "me"}


@user.get("/{uid}/")
async def get_user(uid: int) -> User:
    return await User.get_by_uid(uid)
