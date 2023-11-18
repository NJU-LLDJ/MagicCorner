from fastapi import APIRouter

from api.v1 import v1

api = APIRouter()
api.include_router(v1, prefix="/v1", tags=["v1"])
