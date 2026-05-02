from fastapi import APIRouter
from app.api.v1.endpoints import match

router = APIRouter()
router.include_router(match.router, tags=["match"])