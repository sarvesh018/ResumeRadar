from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import TokenResponse, UserLoginRequest
from app.services.auth_service import AuthService
from resumeradar_common.database.session import get_db

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.login(email=request.email, password=request.password)