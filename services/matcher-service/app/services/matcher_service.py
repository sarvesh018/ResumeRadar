import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.config import get_matcher_settings
from app.repositories.match_repo import MatchRepository
from app.schemas.match import (
    MatchResponse, MatchHistoryResponse, MatchSummaryResponse,
    MissingSkillDetail, SkillMatchDetail, SuggestionDetail,
)
from app.services.jd_parser import parse_jd_skills
from app.services.keyword_matcher import compute_keyword_score
from app.services.semantic_matcher import compute_semantic_score
from app.services.taxonomy_matcher import compute_taxonomy_score

logger = structlog.get_logger()


class MatcherService:
    def __init__(self, db: AsyncSession):
        self.repo = MatchRepository(db)
        self.settings = get_matcher_settings()

    async def match_resume_to_jd(
        self, user_id: UUID, resume_id: UUID, jd_text: str,
        jd_company: str | None = None, jd_role: str | None = None,
        resume_skills: list[dict] | None = None,
        resume_text: str | None = None,
    ) -> MatchResponse:
        jd_skills = parse_jd_skills(jd_text)
        if resume_skills is None:
            resume_skills = []

        keyword_result = compute_keyword_score(resume_skills, jd_skills, self.settings.fuzzy_match_threshold)
        semantic_result = compute_semantic_score(resume_text or "", jd_text, self.settings.semantic_similarity_threshold)
        taxonomy_result = compute_taxonomy_score(resume_skills, jd_skills)

        overall_score = (
            self.settings.keyword_weight * keyword_result["score"]
            + self.settings.semantic_weight * semantic_result["score"]
            + self.settings.taxonomy_weight * taxonomy_result["score"]
        )
        overall_score = round(min(overall_score, 1.0), 4)

        matched_skills = self._build_matched_skills(keyword_result, resume_skills, jd_skills)
        missing_skills = self._build_missing_skills(keyword_result, taxonomy_result)
        suggestions = self._generate_suggestions(missing_skills, taxonomy_result, overall_score)

        match_record = await self.repo.create(
            user_id=user_id, resume_id=resume_id, jd_text=jd_text,
            jd_company=jd_company, jd_role=jd_role,
            keyword_score=keyword_result["score"],
            semantic_score=semantic_result["score"],
            taxonomy_score=taxonomy_result["score"],
            overall_score=overall_score,
            matched_skills=[s.__dict__ if hasattr(s, '__dict__') else s for s in matched_skills],
            missing_skills=[s.__dict__ if hasattr(s, '__dict__') else s for s in missing_skills],
            suggestions=[s.__dict__ if hasattr(s, '__dict__') else s for s in suggestions],
        )

        logger.info("match_completed", user_id=str(user_id), overall_score=overall_score)

        return MatchResponse(
            id=match_record.id, resume_id=resume_id,
            jd_company=jd_company, jd_role=jd_role,
            overall_score=overall_score,
            keyword_score=keyword_result["score"],
            semantic_score=semantic_result["score"],
            taxonomy_score=taxonomy_result["score"],
            matched_skills=matched_skills, missing_skills=missing_skills,
            suggestions=suggestions,
            resume_skill_count=len(resume_skills), jd_skill_count=len(jd_skills),
            created_at=match_record.created_at,
        )

    async def get_match(self, match_id: UUID, user_id: UUID) -> MatchResponse:
        record = await self.repo.get_by_id(match_id, user_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match result not found")

        return MatchResponse(
            id=record.id, resume_id=record.resume_id,
            jd_company=record.jd_company, jd_role=record.jd_role,
            overall_score=record.overall_score,
            keyword_score=record.keyword_score,
            semantic_score=record.semantic_score,
            taxonomy_score=record.taxonomy_score,
            matched_skills=[SkillMatchDetail(**s) for s in (record.matched_skills or [])],
            missing_skills=[MissingSkillDetail(**s) for s in (record.missing_skills or [])],
            suggestions=[SuggestionDetail(**s) for s in (record.suggestions or [])],
            resume_skill_count=0, jd_skill_count=0,
            created_at=record.created_at,
        )

    async def get_history(self, user_id: UUID) -> MatchHistoryResponse:
        records = await self.repo.list_by_user(user_id)
        results = [
            MatchSummaryResponse(
                id=r.id, resume_id=r.resume_id, jd_company=r.jd_company,
                jd_role=r.jd_role, overall_score=r.overall_score, created_at=r.created_at,
            ) for r in records
        ]
        return MatchHistoryResponse(results=results, total=len(results))

    def _build_matched_skills(self, keyword_result, resume_skills, jd_skills):
        details = []
        jd_skill_names = {s["skill_name"] for s in jd_skills}
        for match in keyword_result.get("matched", []):
            details.append(SkillMatchDetail(
                skill=match["skill"], match_type=match["match_type"],
                confidence=match["confidence"], found_in_resume=True, jd_required=True,
            ))
        matched_names = {d.skill for d in details}
        for skill in resume_skills:
            name = skill["skill_name"]
            if name not in matched_names and name not in jd_skill_names:
                details.append(SkillMatchDetail(
                    skill=name, match_type="bonus", confidence=1.0,
                    found_in_resume=True, jd_required=False,
                ))
        return details

    def _build_missing_skills(self, keyword_result, taxonomy_result):
        missing = []
        for skill in keyword_result.get("missing", []):
            suggestion = None
            category = skill.get("category")
            if category:
                suggestion = f"Consider adding '{skill['skill']}' or a similar {category.replace('_', ' ')} tool to your resume."
            missing.append(MissingSkillDetail(
                skill=skill["skill"], category=category,
                importance="required", suggestion=suggestion,
            ))
        return missing

    def _generate_suggestions(self, missing_skills, taxonomy_result, overall_score):
        suggestions = []
        if missing_skills:
            top_missing = [s.skill for s in missing_skills[:5]]
            suggestions.append(SuggestionDetail(
                section="skills", action="add",
                text=f"Add these missing skills to your resume: {', '.join(top_missing)}",
            ))
        missing_cats = taxonomy_result.get("missing_categories", [])
        if missing_cats:
            cat_names = [c.replace("_", " ") for c in missing_cats[:3]]
            suggestions.append(SuggestionDetail(
                section="experience", action="add",
                text=f"Your resume lacks experience in: {', '.join(cat_names)}. Add relevant projects or experience.",
            ))
        if overall_score < 0.5:
            suggestions.append(SuggestionDetail(
                section="summary", action="reword",
                text="This role may not be a strong match. Consider targeting roles that better align with your current skills.",
            ))
        elif overall_score < 0.7:
            suggestions.append(SuggestionDetail(
                section="summary", action="emphasize",
                text="Tailor your resume summary to highlight the skills this role requires. Reword experience bullets to use the JD's terminology.",
            ))
        return suggestions