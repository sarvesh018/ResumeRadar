from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.services.profile_service import ProfileService
from resumeradar_common.auth.dependencies import get_current_user
from resumeradar_common.database.session import get_db

router = APIRouter()


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(user_id: UUID = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = ProfileService(db)
    return await service.get_or_create_profile(user_id)


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(data: ProfileUpdateRequest, user_id: UUID = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    service = ProfileService(db)
    return await service.update_profile(user_id, data)