from app.services.keyword_matcher import compute_keyword_score


class TestKeywordMatcher:
    def test_exact_matches_score_1(self):
        resume = [{"skill_name": "python"}, {"skill_name": "docker"}]
        jd = [{"skill_name": "python"}, {"skill_name": "docker"}]
        result = compute_keyword_score(resume, jd)
        assert result["score"] == 1.0
        assert len(result["matched"]) == 2
        assert len(result["missing"]) == 0
        for match in result["matched"]:
            assert match["confidence"] == 1.0
            assert match["match_type"] == "keyword_exact"

    def test_partial_matches_produce_proportional_score(self):
        resume = [{"skill_name": "python"}, {"skill_name": "docker"}]
        jd = [{"skill_name": "python"}, {"skill_name": "docker"},
              {"skill_name": "terraform"}, {"skill_name": "golang"}]
        result = compute_keyword_score(resume, jd)
        assert result["score"] == 0.5
        assert len(result["matched"]) == 2
        assert len(result["missing"]) == 2

    def test_no_overlap_scores_zero(self):
        resume = [{"skill_name": "python"}, {"skill_name": "react"}]
        jd = [{"skill_name": "golang"}, {"skill_name": "rust"}]
        result = compute_keyword_score(resume, jd)
        assert result["score"] == 0.0

    def test_empty_jd_scores_1(self):
        result = compute_keyword_score([{"skill_name": "python"}], [])
        assert result["score"] == 1.0

    def test_empty_resume_scores_0(self):
        result = compute_keyword_score([], [{"skill_name": "python"}, {"skill_name": "docker"}])
        assert result["score"] == 0.0
        assert len(result["missing"]) == 2

    def test_missing_skills_include_category(self):
        resume = [{"skill_name": "python"}]
        jd = [{"skill_name": "python"}, {"skill_name": "terraform", "category": "infrastructure_as_code"}]
        result = compute_keyword_score(resume, jd)
        assert result["missing"][0]["category"] == "infrastructure_as_code"

    def test_case_insensitive_matching(self):
        result = compute_keyword_score([{"skill_name": "Python"}], [{"skill_name": "python"}])
        assert result["score"] == 1.0