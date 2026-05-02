from app.services.taxonomy_matcher import compute_taxonomy_score


class TestTaxonomyMatcher:
    def test_full_category_coverage_scores_1(self):
        resume = [{"skill_name": "python", "category": "programming_language"},
                  {"skill_name": "docker", "category": "containerization"},
                  {"skill_name": "aws", "category": "cloud_platform"}]
        jd = [{"skill_name": "golang", "category": "programming_language"},
              {"skill_name": "kubernetes", "category": "containerization"},
              {"skill_name": "gcp", "category": "cloud_platform"}]
        result = compute_taxonomy_score(resume, jd)
        assert result["score"] == 1.0

    def test_partial_coverage_scores_proportionally(self):
        resume = [{"skill_name": "python", "category": "programming_language"},
                  {"skill_name": "docker", "category": "containerization"}]
        jd = [{"skill_name": "python", "category": "programming_language"},
              {"skill_name": "docker", "category": "containerization"},
              {"skill_name": "terraform", "category": "infrastructure_as_code"}]
        result = compute_taxonomy_score(resume, jd)
        assert round(result["score"], 2) == 0.67
        assert "infrastructure_as_code" in result["missing_categories"]

    def test_different_tools_same_category_counts(self):
        resume = [{"skill_name": "jenkins", "category": "ci_cd"}]
        jd = [{"skill_name": "github_actions", "category": "ci_cd"}]
        result = compute_taxonomy_score(resume, jd)
        assert result["score"] == 1.0
        assert "ci_cd" in result["covered_categories"]

    def test_no_overlap_scores_zero(self):
        resume = [{"skill_name": "python", "category": "programming_language"}]
        jd = [{"skill_name": "terraform", "category": "infrastructure_as_code"},
              {"skill_name": "grafana", "category": "monitoring"}]
        result = compute_taxonomy_score(resume, jd)
        assert result["score"] == 0.0

    def test_empty_jd_scores_1(self):
        result = compute_taxonomy_score([{"skill_name": "python", "category": "programming_language"}], [])
        assert result["score"] == 1.0

    def test_empty_resume_scores_0(self):
        result = compute_taxonomy_score([], [{"skill_name": "python", "category": "programming_language"}])
        assert result["score"] == 0.0

    def test_category_details_show_tool_mapping(self):
        resume = [{"skill_name": "jenkins", "category": "ci_cd"},
                  {"skill_name": "github_actions", "category": "ci_cd"}]
        jd = [{"skill_name": "gitlab_ci", "category": "ci_cd"}]
        result = compute_taxonomy_score(resume, jd)
        details = result["category_details"]["ci_cd"]
        assert details["covered"] is True
        assert "gitlab_ci" in details["jd_skills"]
        assert "jenkins" in details["resume_skills"]

    def test_skills_without_category_ignored(self):
        resume = [{"skill_name": "python", "category": "programming_language"},
                  {"skill_name": "unknown_tool"}]
        jd = [{"skill_name": "golang", "category": "programming_language"},
              {"skill_name": "another_tool"}]
        result = compute_taxonomy_score(resume, jd)
        assert result["score"] == 1.0