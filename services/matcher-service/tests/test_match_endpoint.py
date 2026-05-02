from uuid import uuid4

SAMPLE_JD = """
Senior DevOps Engineer at TechCorp

Required Skills:
- Strong Python and Bash scripting experience
- Docker and Kubernetes container management
- CI/CD pipeline design with Jenkins or GitHub Actions
- AWS cloud services (EC2, S3, IAM)
- Infrastructure as Code with Terraform
- Monitoring with Grafana and Prometheus
- Linux system administration
- PostgreSQL database management

Nice to Have:
- Golang experience
- ArgoCD for GitOps workflows
"""


class TestMatchEndpoint:
    def test_post_match_returns_201_with_scores(self, client, auth_headers):
        response = client.post("/api/v1/match", headers=auth_headers, json={
            "resume_id": str(uuid4()),
            "jd_text": SAMPLE_JD,
            "jd_company": "TechCorp",
            "jd_role": "Senior DevOps Engineer",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["jd_company"] == "TechCorp"
        assert 0.0 <= data["overall_score"] <= 1.0
        assert 0.0 <= data["keyword_score"] <= 1.0
        assert data["jd_skill_count"] > 0
        assert data["id"] is not None

    def test_post_match_returns_missing_skills(self, client, auth_headers):
        response = client.post("/api/v1/match", headers=auth_headers, json={
            "resume_id": str(uuid4()), "jd_text": SAMPLE_JD,
        })
        assert response.status_code == 201
        assert len(response.json()["missing_skills"]) > 0

    def test_post_match_returns_suggestions(self, client, auth_headers):
        response = client.post("/api/v1/match", headers=auth_headers, json={
            "resume_id": str(uuid4()), "jd_text": SAMPLE_JD,
        })
        assert response.status_code == 201
        suggestions = response.json()["suggestions"]
        assert len(suggestions) > 0
        for s in suggestions:
            assert "section" in s and "action" in s and "text" in s

    def test_get_match_by_id(self, client, auth_headers):
        create_resp = client.post("/api/v1/match", headers=auth_headers, json={
            "resume_id": str(uuid4()), "jd_text": SAMPLE_JD, "jd_company": "TestCorp",
        })
        match_id = create_resp.json()["id"]
        get_resp = client.get(f"/api/v1/match/{match_id}", headers=auth_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == match_id

    def test_get_nonexistent_match_returns_404(self, client, auth_headers):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/match/{fake_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_match_history_returns_past_results(self, client, auth_headers):
        for company in ["CompanyA", "CompanyB"]:
            client.post("/api/v1/match", headers=auth_headers, json={
                "resume_id": str(uuid4()), "jd_text": SAMPLE_JD, "jd_company": company,
            })
        response = client.get("/api/v1/match/history", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 2

    def test_match_without_auth_returns_401(self, client):
        response = client.post("/api/v1/match", json={
            "resume_id": str(uuid4()), "jd_text": SAMPLE_JD,
        })
        assert response.status_code == 401

    def test_match_with_short_jd_returns_422(self, client, auth_headers):
        response = client.post("/api/v1/match", headers=auth_headers, json={
            "resume_id": str(uuid4()), "jd_text": "Too short",
        })
        assert response.status_code == 422