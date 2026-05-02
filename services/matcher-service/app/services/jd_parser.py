import re
import json
from pathlib import Path

import structlog
from rapidfuzz import fuzz

logger = structlog.get_logger()

_SKILL_DICT = None


def _load_skill_dictionary() -> list[dict]:
    global _SKILL_DICT
    if _SKILL_DICT is not None:
        return _SKILL_DICT

    for path in [
        Path(__file__).parent.parent / "data" / "skill_dictionary.json",
        Path(__file__).parent.parent.parent.parent / "profile-service" / "app" / "data" / "skill_dictionary.json",
    ]:
        if path.exists():
            with open(path) as f:
                _SKILL_DICT = json.load(f)["skills"]
            logger.info("jd_skill_dictionary_loaded", skill_count=len(_SKILL_DICT))
            return _SKILL_DICT

    logger.error("skill_dictionary_not_found")
    return []


def parse_jd_skills(jd_text: str) -> list[dict]:
    if not jd_text or len(jd_text.strip()) < 20:
        return []

    found_skills: dict[str, dict] = {}
    normalized = jd_text.lower().strip()
    skill_dict = _load_skill_dictionary()

    for skill_entry in skill_dict:
        canonical = skill_entry["canonical"]
        category = skill_entry["category"]
        search_terms = [canonical] + skill_entry.get("aliases", [])

        for term in search_terms:
            term_lower = term.lower()
            if term_lower in normalized:
                pattern = r'(?<![a-zA-Z])' + re.escape(term_lower) + r'(?![a-zA-Z])'
                if re.search(pattern, normalized):
                    if canonical not in found_skills:
                        found_skills[canonical] = {
                            "skill_name": canonical,
                            "category": category,
                            "confidence": 1.0,
                        }
                    break

    words = set(re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#._-]{1,30}\b', jd_text))
    for word in words:
        word_lower = word.lower()
        if len(word_lower) < 3:
            continue
        for skill_entry in skill_dict:
            canonical = skill_entry["canonical"]
            if canonical in found_skills:
                continue
            all_terms = [canonical] + skill_entry.get("aliases", [])
            for term in all_terms:
                score = fuzz.ratio(word_lower, term.lower())
                if score > 85 and score < 100:
                    found_skills[canonical] = {
                        "skill_name": canonical,
                        "category": skill_entry["category"],
                        "confidence": round(score / 100, 2),
                    }
                    break

    result = list(found_skills.values())
    result.sort(key=lambda s: (-s["confidence"], s["skill_name"]))
    logger.info("jd_skills_extracted", total_found=len(result))
    return result