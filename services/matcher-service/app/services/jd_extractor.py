"""
JD Skill Extractor
===================
Extracts technical skills from a job description text.

Two modes:
1. GROQ (preferred): Uses Llama 3 via free Groq API.
   Returns clean JSON array, handles abbreviations, synonyms.
2. FALLBACK: Uses spaCy NER + skill dictionary.
   No API key needed, slightly less accurate.

Usage:
    skills = await extract_skills_from_jd(jd_text, groq_api_key)
"""

import json
import re
import logging
from typing import Optional

import spacy

logger = logging.getLogger(__name__)

# Load spaCy model once at module level
try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except OSError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy en_core_web_sm not found. Install with: python -m spacy download en_core_web_sm")


# Comprehensive tech skill patterns for spaCy fallback
TECH_SKILL_PATTERNS = [
    # Languages
    "python", "java", "javascript", "typescript", "golang", "go", "rust",
    "c++", "c#", "ruby", "php", "scala", "kotlin", "swift", "r",
    # Web
    "react", "angular", "vue", "node.js", "nodejs", "django", "fastapi",
    "flask", "spring", "express", "nextjs", "graphql", "rest", "rest api",
    "restful", "soap", "grpc",
    # DevOps / Cloud
    "docker", "kubernetes", "k8s", "helm", "terraform", "ansible",
    "jenkins", "github actions", "gitlab ci", "ci/cd", "aws", "gcp",
    "azure", "ec2", "s3", "rds", "lambda", "ecs", "eks", "gke",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "oracle", "sql server", "sqlite", "neo4j",
    "kafka", "rabbitmq", "celery",
    # ML / AI
    "machine learning", "deep learning", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "nlp", "computer vision",
    "llm", "openai", "langchain", "huggingface",
    # Monitoring
    "grafana", "prometheus", "datadog", "splunk", "elk stack",
    "kibana", "logstash",
    # Other
    "git", "linux", "bash", "shell scripting", "microservices",
    "api gateway", "nginx", "apache", "websockets", "oauth",
    "jwt", "ssl", "tls",
]


async def extract_skills_from_jd(
    jd_text: str,
    groq_api_key: Optional[str] = None,
    groq_model: str = "llama3-8b-8192",
) -> list[str]:
    """
    Main entry point: extract skills from JD text.
    Returns a list of lowercase skill names.
    """
    if groq_api_key:
        try:
            skills = await _extract_with_groq(jd_text, groq_api_key, groq_model)
            if skills:
                logger.info(f"Groq extracted {len(skills)} skills from JD")
                return skills
        except Exception as e:
            logger.warning(f"Groq extraction failed, falling back to spaCy: {e}")

    # Fallback
    skills = _extract_with_spacy_and_patterns(jd_text)
    logger.info(f"spaCy/pattern extracted {len(skills)} skills from JD")
    return skills


async def _extract_with_groq(
    jd_text: str,
    api_key: str,
    model: str,
) -> list[str]:
    """
    Use Groq's free Llama 3 to extract skills as structured JSON.

    Groq free tier: 30 req/min, 14,400 req/day
    Sign up at: https://console.groq.com (no credit card)
    """
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("Install groq: pip install groq")

    client = Groq(api_key=api_key)

    # Truncate to avoid token limits (Groq's free tier has 8k context)
    jd_truncated = jd_text[:4000] if len(jd_text) > 4000 else jd_text

    prompt = f"""Extract all technical skills, tools, technologies, and programming languages from this job description.

Return ONLY a JSON array of skill names (strings). No explanation, no markdown, just the JSON array.
Normalize skill names: use "Python" not "python3", "Kubernetes" not "K8s", "Node.js" not "NodeJS".
Include: programming languages, frameworks, databases, cloud platforms, DevOps tools, ML libraries.
Exclude: soft skills (communication, teamwork), generic terms (experience, knowledge, ability).

Job Description:
{jd_truncated}

JSON array:"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500,
    )

    raw = response.choices[0].message.content.strip()

    # Parse JSON — handle cases where model adds extra text
    # Try to find [...] in the response
    json_match = re.search(r'\[.*?\]', raw, re.DOTALL)
    if json_match:
        skills = json.loads(json_match.group())
        # Normalize to lowercase for consistent matching
        return [s.lower().strip() for s in skills if isinstance(s, str) and s.strip()]

    return []


def _extract_with_spacy_and_patterns(jd_text: str) -> list[str]:
    """
    Pattern-based extraction using spaCy + predefined skill list.
    No API key required.
    """
    jd_lower = jd_text.lower()
    found = set()

    # 1. Dictionary pattern matching (multi-word first to avoid partial matches)
    sorted_patterns = sorted(TECH_SKILL_PATTERNS, key=len, reverse=True)
    for pattern in sorted_patterns:
        # Use word-boundary matching for single words, substring for multi-word
        if " " in pattern:
            if pattern in jd_lower:
                found.add(pattern)
        else:
            if re.search(r'\b' + re.escape(pattern) + r'\b', jd_lower):
                found.add(pattern)

    # 2. spaCy NER to catch proper nouns that might be tech tools
    if SPACY_AVAILABLE:
        doc = nlp(jd_text[:5000])
        for ent in doc.ents:
            if ent.label_ in ("PRODUCT", "ORG", "GPE"):
                candidate = ent.text.lower().strip()
                if 2 < len(candidate) < 30 and not candidate.isdigit():
                    found.add(candidate)

    # 3. Extract version-like patterns: "Python 3", "Java 17", "Node 18"
    version_pattern = re.findall(
        r'\b(python|java|node|ruby|php|golang|rust)\s*\d+[\.\d]*\b',
        jd_lower
    )
    for match in version_pattern:
        found.add(match.split()[0])  # Just the language name

    return sorted(list(found))