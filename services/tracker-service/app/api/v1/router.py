from fastapi import APIRouter
from app.api.v1.endpoints import applications

router = APIRouter()
router.include_router(applications.router, tags=["applications"])