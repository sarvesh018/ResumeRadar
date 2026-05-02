from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.resume import (
    ResumeDetailResponse,
    ResumeListResponse,
    ResumeUploadResponse,
    SkillResponse,
)
from app.services.resume_service import ResumeService
from resumeradar_common.auth.dependencies import get_current_user
from resumeradar_common.database.session import get_db
from resumeradar_common.schemas.pagination import MessageResponse

router = APIRouter()


@router.post(
    "/resumes/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file (PDF or DOCX)"),
    version_name: str = Form(
        ...,
        description="Label for this resume version",
        max_length=100,
    ),
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    resume = await service.upload_and_parse(user_id, file, version_name)
    return ResumeUploadResponse(resume=resume)


@router.get("/resumes", response_model=ResumeListResponse)
async def list_resumes(
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    return await service.list_resumes(user_id)


@router.get("/resumes/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    return await service.get_resume(resume_id, user_id)


@router.delete(
    "/resumes/{resume_id}",
    response_model=MessageResponse,
)
async def delete_resume(
    resume_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    await service.delete_resume(resume_id, user_id)
    return MessageResponse(message="Resume deleted successfully")


@router.get("/resumes/{resume_id}/skills", response_model=list[SkillResponse])
async def get_resume_skills(
    resume_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    return await service.get_resume_skills(resume_id, user_id)