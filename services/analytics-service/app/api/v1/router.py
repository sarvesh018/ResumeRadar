from fastapi import APIRouter
from app.api.v1.endpoints import analytics

router = APIRouter()
router.include_router(analytics.router, tags=["analytics"])