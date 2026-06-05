"""
Scoring Engine
===============
Replaces the old full-text semantic comparison with skill-level matching.

Old problem:
  encode(full_resume_text) vs encode(full_jd_text) → always ~0.60
  because any two professional documents have similar embeddings

New approach:
  For each required JD skill, find the best matching resume skill
  using per-skill embeddings → meaningful, differentiated scores
"""

import logging
from typing import Optional
import numpy as np
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)

# Skill category taxonomy (same as before)
SKILL_TAXONOMY: dict[str, str] = {
    # Programming Languages
    "python": "programming_language",
    "java": "programming_language",
    "javascript": "programming_language",
    "typescript": "programming_language",
    "golang": "programming_language",
    "go": "programming_language",
    "rust": "programming_language",
    "c++": "programming_language",
    "c#": "programming_language",
    "ruby": "programming_language",
    "php": "programming_language",
    "scala": "programming_language",
    "kotlin": "programming_language",
    # Frameworks
    "react": "frontend_framework",
    "angular": "frontend_framework",
    "vue": "frontend_framework",
    "django": "backend_framework",
    "fastapi": "backend_framework",
    "flask": "backend_framework",
    "spring": "backend_framework",
    "express": "backend_framework",
    "nodejs": "backend_framework",
    "node.js": "backend_framework",
    # DevOps / CI-CD
    "docker": "containerization",
    "kubernetes": "container_orchestration",
    "k8s": "container_orchestration",
    "helm": "container_orchestration",
    "jenkins": "ci_cd",
    "github actions": "ci_cd",
    "gitlab ci": "ci_cd",
    "ci/cd": "ci_cd",
    "terraform": "infrastructure_as_code",
    "ansible": "infrastructure_as_code",
    "puppet": "infrastructure_as_code",
    # Cloud
    "aws": "cloud_platform",
    "gcp": "cloud_platform",
    "azure": "cloud_platform",
    "ec2": "cloud_compute",
    "s3": "cloud_storage",
    "rds": "cloud_database",
    "lambda": "serverless",
    "ecs": "container_service",
    "eks": "container_service",
    # Databases
    "postgresql": "relational_db",
    "mysql": "relational_db",
    "sqlite": "relational_db",
    "mongodb": "nosql_db",
    "cassandra": "nosql_db",
    "dynamodb": "nosql_db",
    "redis": "cache",
    "elasticsearch": "search_engine",
    "kafka": "message_queue",
    "rabbitmq": "message_queue",
    # Monitoring
    "grafana": "monitoring",
    "prometheus": "monitoring",
    "datadog": "monitoring",
    "splunk": "log_management",
    # ML
    "tensorflow": "ml_framework",
    "pytorch": "ml_framework",
    "scikit-learn": "ml_library",
    "pandas": "data_processing",
    "numpy": "data_processing",
}


def get_category(skill: str) -> Optional[str]:
    """Look up skill category, try common normalizations."""
    skill = skill.lower().strip()
    return (
        SKILL_TAXONOMY.get(skill)
        or SKILL_TAXONOMY.get(skill.replace("-", ""))
        or SKILL_TAXONOMY.get(skill.replace(".", ""))
        or SKILL_TAXONOMY.get(skill.replace(" ", ""))
    )


def compute_keyword_score(
    jd_skills: list[str],
    resume_skills: list[str],
    fuzzy_threshold: int = 85,
) -> tuple[float, list[dict], list[dict]]:
    """
    Layer 1: Fuzzy keyword matching between JD skills and resume skills.

    Returns:
        score: 0.0 to 1.0
        matched: list of matched skill details
        missing: list of missing skill details
    """
    if not jd_skills:
        return 0.0, [], []

    jd_norm = [s.lower().strip() for s in jd_skills]
    resume_norm = [s.lower().strip() for s in resume_skills]

    matched = []
    missing = []

    for jd_skill in jd_norm:
        best_score = 0
        best_match = None

        for res_skill in resume_norm:
            # Exact match
            if jd_skill == res_skill:
                best_score = 100
                best_match = res_skill
                break
            # Fuzzy match (handles "K8s" ~ "Kubernetes", "Postgres" ~ "PostgreSQL")
            ratio = fuzz.ratio(jd_skill, res_skill)
            partial = fuzz.partial_ratio(jd_skill, res_skill)
            score = max(ratio, partial)
            if score > best_score:
                best_score = score
                best_match = res_skill

        if best_score >= fuzzy_threshold:
            matched.append({
                "skill": jd_skill,
                "matched_with": best_match,
                "match_type": "exact" if best_score == 100 else "fuzzy",
                "confidence": best_score / 100,
                "found_in_resume": True,
                "jd_required": True,
            })
        else:
            category = get_category(jd_skill)
            missing.append({
                "skill": jd_skill,
                "category": category,
                "importance": "required",
                "suggestion": f"Add '{jd_skill}' or a related {category or 'skill'} to your resume.",
            })

    score = len(matched) / len(jd_norm) if jd_norm else 0.0
    return round(score, 3), matched, missing


def compute_semantic_skill_score(
    jd_skills: list[str],
    resume_skills: list[str],
    model,  # SentenceTransformer instance
    threshold: float = 0.65,
) -> float:
    """
    Layer 2: Semantic skill-to-skill matching.

    Instead of comparing full document text (which always gives ~0.6),
    we compare each JD skill against all resume skills and take the
    best semantic match for each.

    Example:
        JD skill: "K8s"
        Resume skills: ["Kubernetes", "Docker", "Helm"]
        Best match: "Kubernetes" at 0.89 similarity ✓

        JD skill: "Terraform"
        Resume skills: ["Python", "SQL", "Jenkins"]
        Best match: "Jenkins" at 0.58 similarity → below threshold ✗
    """
    if not jd_skills or not resume_skills:
        return 0.0

    try:
        from sklearn.metrics.pairwise import cosine_similarity

        # Encode all skills at once (batched is faster)
        all_skills = jd_skills + resume_skills
        embeddings = model.encode(all_skills, batch_size=32, show_progress_bar=False)

        jd_embeddings = embeddings[:len(jd_skills)]
        resume_embeddings = embeddings[len(jd_skills):]

        # For each JD skill, find the best matching resume skill
        similarities = cosine_similarity(jd_embeddings, resume_embeddings)

        scores = []
        for i, jd_skill in enumerate(jd_skills):
            best_sim = float(np.max(similarities[i]))
            # Only count if above threshold
            scores.append(best_sim if best_sim >= threshold else 0.0)

        return round(float(np.mean(scores)), 3)

    except Exception as e:
        logger.warning(f"Semantic skill scoring failed: {e}")
        return 0.0


def compute_taxonomy_score(
    jd_skills: list[str],
    resume_skills: list[str],
) -> float:
    """
    Layer 3: Category-level matching.

    Gives partial credit when user has tools in the same category.
    Example: JD requires "Prometheus" (monitoring), user has "Datadog" (monitoring)
    → full category credit even without exact skill match.
    """
    if not jd_skills:
        return 0.0

    jd_categories = {
        get_category(s) for s in jd_skills if get_category(s)
    }
    resume_categories = {
        get_category(s) for s in resume_skills if get_category(s)
    }

    if not jd_categories:
        return 0.5  # Unknown categories → neutral

    matched_categories = jd_categories & resume_categories
    return round(len(matched_categories) / len(jd_categories), 3)


def compute_final_score(
    keyword_score: float,
    semantic_score: float,
    taxonomy_score: float,
    weight_keyword: float = 0.50,
    weight_semantic: float = 0.30,
    weight_taxonomy: float = 0.20,
) -> float:
    """Weighted combination of the three layers."""
    score = (
        weight_keyword * keyword_score
        + weight_semantic * semantic_score
        + weight_taxonomy * taxonomy_score
    )
    return round(min(max(score, 0.0), 1.0), 3)


def generate_suggestions(
    missing_skills: list[dict],
    matched_skills: list[dict],
    overall_score: float,
) -> list[dict]:
    """Generate actionable improvement suggestions."""
    suggestions = []

    # Missing skills suggestion
    if missing_skills:
        required_missing = [s["skill"] for s in missing_skills if s.get("importance") == "required"]
        if required_missing:
            top = required_missing[:5]
            suggestions.append({
                "section": "skills",
                "action": "add",
                "text": f"Add these skills to close the gap: {', '.join(top)}",
            })

    # Category gap suggestion
    missing_categories = {}
    for skill in missing_skills:
        cat = skill.get("category")
        if cat:
            missing_categories.setdefault(cat, []).append(skill["skill"])

    for category, skills in list(missing_categories.items())[:2]:
        suggestions.append({
            "section": "skills",
            "action": "add",
            "text": f"You're missing skills in {category.replace('_', ' ')}: {', '.join(skills[:3])}",
        })

    # Score-based advice
    if overall_score < 0.5:
        suggestions.append({
            "section": "summary",
            "action": "rewrite",
            "text": "Your profile matches fewer than half the JD requirements. Consider tailoring your resume for this specific role.",
        })
    elif overall_score < 0.7:
        suggestions.append({
            "section": "experience",
            "action": "emphasize",
            "text": "You have a decent match. Highlight projects where you used the matching skills to strengthen your application.",
        })
    else:
        suggestions.append({
            "section": "application",
            "action": "apply",
            "text": "Strong match! Make sure your experience section explicitly mentions these skills in context.",
        })

    return suggestions