from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import RegisterResponse, UserRegisterRequest
from app.services.auth_service import AuthService
from resumeradar_common.database.session import get_db

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.register(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )
    return RegisterResponse(user=user)