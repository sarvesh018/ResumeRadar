import json
import re
from pathlib import Path

import structlog
from rapidfuzz import fuzz

logger = structlog.get_logger()

_SKILL_DICT = None


def _load_skill_dictionary() -> list[dict]:
    global _SKILL_DICT
    if _SKILL_DICT is not None:
        return _SKILL_DICT
    dict_path = Path(__file__).parent.parent / "data" / "skill_dictionary.json"
    try:
        with open(dict_path) as f:
            data = json.load(f)
        _SKILL_DICT = data["skills"]
        logger.info("skill_dictionary_loaded", skill_count=len(_SKILL_DICT))
        return _SKILL_DICT
    except FileNotFoundError:
        logger.error("skill_dictionary_not_found", path=str(dict_path))
        return []


def _normalize_text(text: str) -> str:
    return text.lower().strip()


def extract_skills_from_text(text: str) -> list[dict]:
    if not text or len(text.strip()) < 10:
        return []

    found_skills: dict[str, dict] = {}
    normalized_text = _normalize_text(text)
    skill_dict = _load_skill_dictionary()

    # Pass 1: Dictionary matching
    for skill_entry in skill_dict:
        canonical = skill_entry["canonical"]
        category = skill_entry["category"]
        search_terms = [canonical] + skill_entry.get("aliases", [])

        for term in search_terms:
            term_lower = term.lower()
            if term_lower in normalized_text:
                pattern = r'(?<![a-zA-Z])' + re.escape(term_lower) + r'(?![a-zA-Z])'
                if re.search(pattern, normalized_text):
                    if canonical not in found_skills:
                        found_skills[canonical] = {
                            "skill_name": canonical,
                            "category": category,
                            "confidence": 1.0,
                        }
                    break

    # Pass 2: Fuzzy matching for near-misses
    words = set(re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#._-]{1,30}\b', text))
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
    logger.info("skills_extracted", total_found=len(result))
    return result