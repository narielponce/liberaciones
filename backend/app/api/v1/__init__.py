from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.machines import router as machines_router
from app.api.v1.releases import router as releases_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(machines_router)
api_v1_router.include_router(releases_router)
