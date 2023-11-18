from fastapi import APIRouter

from api.v1.user import user

v1 = APIRouter()
v1.include_router(user, prefix="/user", tags=["user"])
