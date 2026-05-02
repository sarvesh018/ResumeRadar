import structlog

logger = structlog.get_logger()


def compute_taxonomy_score(
    resume_skills: list[dict],
    jd_skills: list[dict],
) -> dict:
    if not jd_skills:
        return {"score": 1.0, "covered_categories": [], "missing_categories": [], "category_details": {}}

    if not resume_skills:
        jd_categories = set()
        for s in jd_skills:
            cat = s.get("category")
            if cat:
                jd_categories.add(cat)
        return {"score": 0.0, "covered_categories": [], "missing_categories": list(jd_categories), "category_details": {}}

    jd_by_category: dict[str, list[str]] = {}
    for skill in jd_skills:
        cat = skill.get("category")
        if cat:
            if cat not in jd_by_category:
                jd_by_category[cat] = []
            jd_by_category[cat].append(skill["skill_name"])

    resume_by_category: dict[str, list[str]] = {}
    for skill in resume_skills:
        cat = skill.get("category")
        if cat:
            if cat not in resume_by_category:
                resume_by_category[cat] = []
            resume_by_category[cat].append(skill["skill_name"])

    covered = []
    missing = []
    category_details = {}

    for cat, jd_skill_list in jd_by_category.items():
        resume_skill_list = resume_by_category.get(cat, [])
        is_covered = len(resume_skill_list) > 0
        category_details[cat] = {
            "jd_skills": jd_skill_list,
            "resume_skills": resume_skill_list,
            "covered": is_covered,
        }
        if is_covered:
            covered.append(cat)
        else:
            missing.append(cat)

    score = len(covered) / len(jd_by_category) if jd_by_category else 1.0

    logger.info("taxonomy_matching_done", score=round(score, 3), covered=len(covered), missing=len(missing))

    return {
        "score": round(score, 4),
        "covered_categories": covered,
        "missing_categories": missing,
        "category_details": category_details,
    }