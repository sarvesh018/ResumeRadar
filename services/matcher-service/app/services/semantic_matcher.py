import structlog

logger = structlog.get_logger()

_model = None
_model_load_attempted = False


def _get_model():
    global _model, _model_load_attempted
    if _model is not None:
        return _model
    if _model_load_attempted:
        return None
    _model_load_attempted = True
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("embedding_model_loaded", model="all-MiniLM-L6-v2")
        return _model
    except ImportError:
        logger.warning("sentence_transformers_not_installed")
        return None
    except Exception as e:
        logger.error("embedding_model_load_failed", error=str(e))
        return None


def _cosine_similarity(vec_a, vec_b) -> float:
    import numpy as np
    dot = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def _split_into_chunks(text: str, max_chunk_length: int = 200) -> list[str]:
    lines = text.replace("\u2022", "\n").replace("- ", "\n").split("\n")
    chunks = []
    for line in lines:
        line = line.strip()
        if len(line) > 20:
            if len(line) > max_chunk_length:
                sentences = line.replace(". ", ".\n").split("\n")
                chunks.extend(s.strip() for s in sentences if len(s.strip()) > 20)
            else:
                chunks.append(line)
    return chunks


def compute_semantic_score(
    resume_text: str,
    jd_text: str,
    threshold: float = 0.5,
) -> dict:
    if not resume_text or not jd_text:
        return {"score": 0.0, "top_matches": []}

    model = _get_model()
    if model is None:
        logger.warning("semantic_matching_skipped", reason="model not available")
        return {"score": 0.0, "top_matches": []}

    resume_chunks = _split_into_chunks(resume_text)
    jd_chunks = _split_into_chunks(jd_text)

    if not resume_chunks or not jd_chunks:
        return {"score": 0.0, "top_matches": []}

    resume_embeddings = model.encode(resume_chunks, show_progress_bar=False)
    jd_embeddings = model.encode(jd_chunks, show_progress_bar=False)

    top_matches = []
    jd_scores = []

    for i, jd_emb in enumerate(jd_embeddings):
        best_sim = 0.0
        best_resume_idx = 0
        for j, resume_emb in enumerate(resume_embeddings):
            sim = _cosine_similarity(jd_emb, resume_emb)
            if sim > best_sim:
                best_sim = sim
                best_resume_idx = j
        jd_scores.append(best_sim)
        if best_sim >= threshold:
            top_matches.append({
                "resume_chunk": resume_chunks[best_resume_idx][:100],
                "jd_chunk": jd_chunks[i][:100],
                "similarity": round(best_sim, 3),
            })

    overall = sum(jd_scores) / len(jd_scores) if jd_scores else 0.0
    top_matches.sort(key=lambda m: -m["similarity"])

    logger.info("semantic_matching_done", score=round(overall, 3), above_threshold=len(top_matches))

    return {"score": round(overall, 4), "top_matches": top_matches[:10]}