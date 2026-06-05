"""
Matcher Service
================
Orchestrates the full match pipeline:
1. Extract skills from JD (Groq or spaCy)
2. Load resume skills from DB
3. Fetch profile skills from profile-service (supplement)
4. Run 3-layer scoring
5. Save result
"""

import logging
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sentence_transformers import SentenceTransformer

from ..core.config import settings
from ..models.match_result import MatchResult
from ..repositories.match_repo import MatchRepository
from ..schemas.match import MatchRequest, MatchResponse
from .jd_extractor import extract_skills_from_jd
from .scoring import (
    compute_keyword_score,
    compute_semantic_skill_score,
    compute_taxonomy_score,
    compute_final_score,
    generate_suggestions,
)

logger = logging.getLogger(__name__)

# Load model once at startup (heavy operation)
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Model loaded")
    return _model


class MatcherService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MatchRepository(db)

    async def match_resume_to_jd(
        self,
        user_id: UUID,
        request: MatchRequest,
    ) -> MatchResponse:
        # 1. Load resume skills from DB
        resume_skills = await self._get_resume_skills(request.resume_id)
        logger.info(f"Resume has {len(resume_skills)} skills")

        # 2. Fetch profile skills from profile-service to supplement
        profile_skills = await self._get_profile_skills(user_id)
        logger.info(f"Profile has {len(profile_skills)} skills")

        # 3. Combine: resume skills + profile skills (deduplicated)
        all_resume_skills = list({
            s.lower().strip()
            for s in resume_skills + profile_skills
            if s.strip()
        })
        logger.info(f"Combined skills for matching: {len(all_resume_skills)}")

        # 4. Extract skills from JD using Groq or spaCy
        jd_skills = await extract_skills_from_jd(
            jd_text=request.jd_text,
            groq_api_key=settings.groq_api_key,
            groq_model=settings.groq_model,
        )
        logger.info(f"JD has {len(jd_skills)} extracted skills: {jd_skills[:10]}")

        if not jd_skills:
            # If we extracted nothing, use basic text-level matching
            jd_skills = self._basic_skill_extract(request.jd_text)
            logger.warning(f"Using basic extraction, found {len(jd_skills)} skills")

        # 5. Layer 1: Keyword score
        keyword_score, matched_skills, missing_skills = compute_keyword_score(
            jd_skills=jd_skills,
            resume_skills=all_resume_skills,
            fuzzy_threshold=85,
        )

        # 6. Layer 2: Semantic skill-to-skill score
        # Only run on skills that did NOT match in Layer 1
        unmatched_jd_skills = [s["skill"] for s in missing_skills]
        if unmatched_jd_skills and all_resume_skills:
            semantic_score = compute_semantic_skill_score(
                jd_skills=unmatched_jd_skills,
                resume_skills=all_resume_skills,
                model=get_model(),
                threshold=settings.semantic_match_threshold,
            )
        else:
            semantic_score = 1.0 if not unmatched_jd_skills else 0.0

        # 7. Layer 3: Taxonomy/category score
        taxonomy_score = compute_taxonomy_score(
            jd_skills=jd_skills,
            resume_skills=all_resume_skills,
        )

        # 8. Final weighted score
        overall_score = compute_final_score(
            keyword_score=keyword_score,
            semantic_score=semantic_score,
            taxonomy_score=taxonomy_score,
            weight_keyword=settings.weight_keyword,
            weight_semantic=settings.weight_semantic,
            weight_taxonomy=settings.weight_taxonomy,
        )

        logger.info(
            f"Scores — keyword: {keyword_score}, semantic: {semantic_score}, "
            f"taxonomy: {taxonomy_score}, overall: {overall_score}"
        )

        # 9. Suggestions
        suggestions = generate_suggestions(missing_skills, matched_skills, overall_score)

        # 10. Save to DB
        result = await self.repo.create(
            user_id=user_id,
            resume_id=request.resume_id,
            jd_text=request.jd_text,
            jd_company=request.jd_company,
            jd_role=request.jd_role,
            keyword_score=keyword_score,
            semantic_score=semantic_score,
            taxonomy_score=taxonomy_score,
            overall_score=overall_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            suggestions=suggestions,
            resume_skill_count=len(resume_skills),
            jd_skill_count=len(jd_skills),
        )

        return MatchResponse.model_validate(result)

    async def _get_resume_skills(self, resume_id: UUID) -> list[str]:
        """Fetch skills extracted from the resume (stored in profile-service DB)."""
        try:
            skills = await self.repo.get_resume_skills(resume_id)
            return [s.skill_name for s in skills]
        except Exception as e:
            logger.error(f"Failed to fetch resume skills: {e}")
            return []

    async def _get_profile_skills(self, user_id: UUID) -> list[str]:
        """
        Fetch skills from user's profile via HTTP to profile-service.
        These are skills the user manually added to their profile.
        Returns empty list if profile-service is unreachable (non-blocking).
        """
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(
                    f"{settings.profile_service_url}/api/v1/profile",
                    headers={"X-Internal-User-ID": str(user_id)},
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("technical_skills", []) or []
        except Exception as e:
            logger.warning(f"Could not fetch profile skills (non-critical): {e}")
        return []

    def _basic_skill_extract(self, text: str) -> list[str]:
        """Ultra-basic fallback if both Groq and spaCy fail."""
        from .jd_extractor import TECH_SKILL_PATTERNS
        import re
        text_lower = text.lower()
        found = []
        for pattern in TECH_SKILL_PATTERNS:
            if re.search(r'\b' + re.escape(pattern) + r'\b', text_lower):
                found.append(pattern)
        return found