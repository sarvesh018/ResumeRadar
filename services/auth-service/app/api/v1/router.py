from fastapi import APIRouter

from app.api.v1.endpoints import login, me, register

router = APIRouter()

router.include_router(register.router, tags=["auth"])
router.include_router(login.router, tags=["auth"])
router.include_router(me.router, tags=["auth"])