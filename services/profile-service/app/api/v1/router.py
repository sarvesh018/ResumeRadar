from fastapi import APIRouter
from app.api.v1.endpoints import profile, resumes

router = APIRouter()
router.include_router(profile.router, tags=["profile"])
router.include_router(resumes.router, tags=["resumes"])