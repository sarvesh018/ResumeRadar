import os
import uuid
import structlog
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.config import get_profile_settings
from app.repositories.resume_repo import ResumeRepository
from app.schemas.resume import (
    ResumeDetailResponse,
    ResumeListResponse,
    ResumeResponse,
    SkillResponse,
)
from app.services.resume_parser import extract_text
from app.services.skill_extractor import extract_skills_from_text

logger = structlog.get_logger()


class ResumeService:
    def __init__(self, db: AsyncSession):
        self.repo = ResumeRepository(db)
        self.settings = get_profile_settings()

    async def upload_and_parse(
        self, user_id: UUID, file: UploadFile, version_name: str
    ) -> ResumeDetailResponse:
        # Step 1: Validate file
        file_ext = self._validate_file(file)

        # Step 2: Read file bytes
        file_bytes = await file.read()
        if len(file_bytes) > self.settings.max_file_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds {self.settings.max_file_size_mb}MB limit",
            )

        # Step 3: Store file
        resume_id = uuid.uuid4()
        file_key = f"{self.settings.resume_s3_prefix}/{user_id}/{resume_id}.{file_ext}"
        file_url = self._store_file(file_bytes, file_key)

        # Step 4: Extract text from file
        raw_text = extract_text(file_bytes, file_ext)
        if not raw_text:
            logger.warning("empty_text_extraction", file_type=file_ext, user_id=str(user_id))

        # Step 5: Extract skills from text
        extracted_skills = extract_skills_from_text(raw_text) if raw_text else []

        # Step 6: Save resume metadata to database
        resume = await self.repo.create(
            user_id=user_id,
            version_name=version_name,
            file_url=file_url,
            file_type=file_ext,
            raw_text=raw_text,
        )

        # Save extracted skills
        if extracted_skills:
            await self.repo.add_skills(resume.id, extracted_skills)

        logger.info(
            "resume_uploaded",
            user_id=str(user_id),
            resume_id=str(resume.id),
            file_type=file_ext,
            text_length=len(raw_text),
            skills_found=len(extracted_skills),
        )

        # Build response
        skill_responses = [SkillResponse(**s) for s in extracted_skills]
        return ResumeDetailResponse(
            id=resume.id,
            user_id=resume.user_id,
            version_name=resume.version_name,
            file_type=resume.file_type,
            is_primary=resume.is_primary,
            created_at=resume.created_at,
            updated_at=resume.updated_at,
            skill_count=len(extracted_skills),
            text_length=len(raw_text),
            skills=skill_responses,
        )

    async def list_resumes(self, user_id: UUID) -> ResumeListResponse:
        resumes = await self.repo.list_by_user(user_id)
        resume_responses = [ResumeResponse.model_validate(r) for r in resumes]
        return ResumeListResponse(resumes=resume_responses, total=len(resume_responses))

    async def get_resume(self, resume_id: UUID, user_id: UUID) -> ResumeDetailResponse:
        resume = await self.repo.get_by_id(resume_id, user_id)
        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        skills = await self.repo.get_skills(resume.id)
        skill_responses = [SkillResponse.model_validate(s) for s in skills]

        return ResumeDetailResponse(
            id=resume.id,
            user_id=resume.user_id,
            version_name=resume.version_name,
            file_type=resume.file_type,
            is_primary=resume.is_primary,
            created_at=resume.created_at,
            updated_at=resume.updated_at,
            skill_count=len(skill_responses),
            text_length=len(resume.raw_text) if resume.raw_text else 0,
            skills=skill_responses,
        )

    async def get_resume_skills(self, resume_id: UUID, user_id: UUID) -> list[SkillResponse]:
        resume = await self.repo.get_by_id(resume_id, user_id)
        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        skills = await self.repo.get_skills(resume.id)
        return [SkillResponse.model_validate(s) for s in skills]

    async def delete_resume(self, resume_id: UUID, user_id: UUID) -> None:
        resume = await self.repo.get_by_id(resume_id, user_id)
        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        await self.repo.delete(resume)
        logger.info("resume_deleted", resume_id=str(resume_id), user_id=str(user_id))

    def _validate_file(self, file: UploadFile) -> str:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

        if ext not in self.settings.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '.{ext}'. Allowed: {self.settings.allowed_extensions}",
            )

        return ext

    def _store_file(self, file_bytes: bytes, file_key: str) -> str:
        if self.settings.is_production:
            from resumeradar_common.utils.s3_client import upload_file
            return upload_file(file_bytes, file_key)
        else:
            local_dir = "/tmp/resumeradar_uploads"
            os.makedirs(os.path.dirname(f"{local_dir}/{file_key}"), exist_ok=True)
            full_path = f"{local_dir}/{file_key}"
            with open(full_path, "wb") as f:
                f.write(file_bytes)
            return full_path