from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import UserResponse
from app.services.auth_service import AuthService
from resumeradar_common.auth.dependencies import get_current_user
from resumeradar_common.database.session import get_db

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(user_id: UUID = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.get_current_user(user_id)