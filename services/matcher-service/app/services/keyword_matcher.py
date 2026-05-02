from rapidfuzz import fuzz
import structlog

logger = structlog.get_logger()


def compute_keyword_score(
    resume_skills: list[dict],
    jd_skills: list[dict],
    threshold: int = 80,
) -> dict:
    if not jd_skills:
        return {"score": 1.0, "matched": [], "missing": []}

    if not resume_skills:
        return {
            "score": 0.0,
            "matched": [],
            "missing": [{"skill": s["skill_name"], "category": s.get("category")} for s in jd_skills],
        }

    resume_skill_names = {s["skill_name"].lower() for s in resume_skills}
    matched = []
    missing = []

    for jd_skill in jd_skills:
        jd_name = jd_skill["skill_name"].lower()
        best_match = None
        best_score = 0

        if jd_name in resume_skill_names:
            matched.append({
                "skill": jd_skill["skill_name"],
                "confidence": 1.0,
                "match_type": "keyword_exact",
            })
            continue

        for resume_name in resume_skill_names:
            score = fuzz.ratio(jd_name, resume_name)
            if score > best_score:
                best_score = score
                best_match = resume_name

        if best_score >= threshold:
            matched.append({
                "skill": jd_skill["skill_name"],
                "confidence": round(best_score / 100, 2),
                "match_type": "keyword_fuzzy",
                "matched_with": best_match,
            })
        else:
            missing.append({
                "skill": jd_skill["skill_name"],
                "category": jd_skill.get("category"),
            })

    score = len(matched) / len(jd_skills) if jd_skills else 0.0

    logger.info("keyword_matching_done", score=round(score, 3), matched=len(matched), missing=len(missing))

    return {"score": round(score, 4), "matched": matched, "missing": missing}