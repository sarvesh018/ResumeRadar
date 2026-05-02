from app.services.skill_extractor import extract_skills_from_text


class TestSkillExtraction:
    def test_extracts_programming_languages(self, sample_resume_text):
        """Should find Python, JavaScript, SQL, Bash, C++ from the sample resume."""
        skills = extract_skills_from_text(sample_resume_text)
        skill_names = [s["skill_name"] for s in skills]

        assert "python" in skill_names
        assert "javascript" in skill_names
        assert "sql" in skill_names
        assert "bash" in skill_names
        assert "c++" in skill_names

    def test_extracts_devops_tools(self, sample_resume_text):
        """Should find Docker, Kubernetes, Jenkins, Terraform etc."""
        skills = extract_skills_from_text(sample_resume_text)
        skill_names = [s["skill_name"] for s in skills]

        assert "docker" in skill_names
        assert "kubernetes" in skill_names
        assert "jenkins" in skill_names
        assert "terraform" in skill_names
        assert "helm" in skill_names

    def test_extracts_cloud_services(self, sample_resume_text):
        """Should find AWS and its sub-services."""
        skills = extract_skills_from_text(sample_resume_text)
        skill_names = [s["skill_name"] for s in skills]

        assert "aws" in skill_names
        assert "aws_ec2" in skill_names
        assert "aws_s3" in skill_names

    def test_extracts_monitoring_tools(self, sample_resume_text):
        """Should find Grafana, Prometheus, Alertmanager."""
        skills = extract_skills_from_text(sample_resume_text)
        skill_names = [s["skill_name"] for s in skills]

        assert "grafana" in skill_names
        assert "prometheus" in skill_names
        assert "alertmanager" in skill_names

    def test_normalizes_aliases(self):
        """K8s should be normalized to 'kubernetes'."""
        text = "Managed K8s clusters and wrote Helm charts for deployments."
        skills = extract_skills_from_text(text)
        skill_names = [s["skill_name"] for s in skills]

        assert "kubernetes" in skill_names
        assert "helm" in skill_names
        assert "k8s" not in skill_names

    def test_assigns_categories(self, sample_resume_text):
        """Each skill should have a category assigned."""
        skills = extract_skills_from_text(sample_resume_text)

        python_skill = next(s for s in skills if s["skill_name"] == "python")
        assert python_skill["category"] == "programming_language"

        docker_skill = next(s for s in skills if s["skill_name"] == "docker")
        assert docker_skill["category"] == "containerization"

        k8s_skill = next(s for s in skills if s["skill_name"] == "kubernetes")
        assert k8s_skill["category"] == "container_orchestration"

    def test_dictionary_matches_have_full_confidence(self, sample_resume_text):
        """Exact dictionary matches should have confidence=1.0."""
        skills = extract_skills_from_text(sample_resume_text)

        python_skill = next(s for s in skills if s["skill_name"] == "python")
        assert python_skill["confidence"] == 1.0

    def test_no_duplicate_skills(self, sample_resume_text):
        """Same skill appearing multiple times should be deduplicated."""
        skills = extract_skills_from_text(sample_resume_text)
        skill_names = [s["skill_name"] for s in skills]

        assert len(skill_names) == len(set(skill_names))

    def test_empty_text_returns_empty(self):
        """Empty or very short text should return no skills."""
        assert extract_skills_from_text("") == []
        assert extract_skills_from_text("hello") == []
        assert extract_skills_from_text(None) == []

    def test_word_boundary_matching(self):
        """'go' should NOT match in 'google' or 'going'."""
        text = "I worked at Google on the Go programming language."
        skills = extract_skills_from_text(text)
        skill_names = [s["skill_name"] for s in skills]

        assert "golang" in skill_names

    def test_minimum_skill_count(self, sample_resume_text):
        """A real DevOps resume should extract at least 15 skills."""
        skills = extract_skills_from_text(sample_resume_text)
        assert len(skills) >= 15, f"Only found {len(skills)} skills, expected 15+"

    def test_ci_cd_variations(self):
        """CI/CD should be recognized in various forms."""
        text = "Built CI/CD pipelines and continuous integration workflows."
        skills = extract_skills_from_text(text)
        skill_names = [s["skill_name"] for s in skills]

        assert "ci_cd" in skill_names