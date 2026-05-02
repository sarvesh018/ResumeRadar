from app.services.semantic_matcher import _split_into_chunks, compute_semantic_score


class TestTextChunking:
    def test_splits_by_newlines(self):
        text = "Built CI/CD pipelines using Jenkins\nManaged Kubernetes clusters\nWrote Terraform modules"
        chunks = _split_into_chunks(text)
        assert len(chunks) == 3

    def test_splits_by_bullet_points(self):
        text = "- Built CI/CD pipelines using Jenkins\n- Managed Kubernetes clusters\n- Wrote Terraform modules"
        chunks = _split_into_chunks(text)
        assert len(chunks) == 3

    def test_skips_short_lines(self):
        text = "EXPERIENCE\nBuilt CI/CD pipelines using Jenkins for automated deployment\nEDUCATION\nBachelor of Computer Science from Pune University"
        chunks = _split_into_chunks(text)
        assert all(len(c) > 20 for c in chunks)

    def test_empty_text_returns_empty(self):
        assert _split_into_chunks("") == []
        assert _split_into_chunks("   ") == []


class TestSemanticScoreFallback:
    def test_empty_inputs_return_zero(self):
        assert compute_semantic_score("", "Some JD text here")["score"] == 0.0
        assert compute_semantic_score("Some resume text", "")["score"] == 0.0

    def test_both_empty_returns_zero(self):
        assert compute_semantic_score("", "")["score"] == 0.0

    def test_returns_dict_with_expected_keys(self):
        result = compute_semantic_score("resume text here", "jd text here")
        assert "score" in result
        assert "top_matches" in result
        assert isinstance(result["score"], float)
        assert isinstance(result["top_matches"], list)