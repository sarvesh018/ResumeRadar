class TestDashboard:
    def test_dashboard_returns_correct_totals(self, client, auth_headers):
        response = client.get("/api/v1/analytics/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_applications"] == 10
        assert data["active_applications"] == 7   # 10 - 3 rejected
        assert data["response_rate"] == 0.5        # 5/10
        assert data["interview_rate"] == 0.3       # 3/10
        assert data["offer_rate"] == 0.1           # 1/10

    def test_dashboard_shows_avg_match_score(self, client, auth_headers):
        data = client.get("/api/v1/analytics/dashboard", headers=auth_headers).json()
        assert data["avg_match_score"] is not None
        assert 0.0 < data["avg_match_score"] < 1.0

    def test_dashboard_shows_top_company(self, client, auth_headers):
        data = client.get("/api/v1/analytics/dashboard", headers=auth_headers).json()
        assert data["most_applied_company"] is not None

    def test_dashboard_shows_top_role(self, client, auth_headers):
        data = client.get("/api/v1/analytics/dashboard", headers=auth_headers).json()
        assert data["most_applied_role"] == "DevOps Engineer"

    def test_dashboard_without_auth_returns_401(self, client):
        assert client.get("/api/v1/analytics/dashboard").status_code == 401


class TestFunnel:
    def test_funnel_has_all_stages(self, client, auth_headers):
        data = client.get("/api/v1/analytics/funnel", headers=auth_headers).json()
        statuses = [s["status"] for s in data["stages"]]
        assert "applied" in statuses
        assert "screening" in statuses
        assert "interviewing" in statuses
        assert "offer" in statuses
        assert "rejected" in statuses

    def test_funnel_counts_are_correct(self, client, auth_headers):
        data = client.get("/api/v1/analytics/funnel", headers=auth_headers).json()
        stage_map = {s["status"]: s["count"] for s in data["stages"]}
        assert stage_map["applied"] == 2
        assert stage_map["screening"] == 2
        assert stage_map["interviewing"] == 2
        assert stage_map["offer"] == 1
        assert stage_map["rejected"] == 3

    def test_funnel_total_matches(self, client, auth_headers):
        data = client.get("/api/v1/analytics/funnel", headers=auth_headers).json()
        assert data["total_applications"] == 10

    def test_funnel_rates_are_correct(self, client, auth_headers):
        data = client.get("/api/v1/analytics/funnel", headers=auth_headers).json()
        assert data["overall_response_rate"] == 0.5
        assert data["offer_rate"] == 0.1


class TestResumeComparison:
    def test_shows_two_resume_versions(self, client, auth_headers):
        data = client.get("/api/v1/analytics/resumes", headers=auth_headers).json()
        assert len(data["versions"]) == 2

    def test_resume_v2_outperforms_v1(self, client, auth_headers):
        data = client.get("/api/v1/analytics/resumes", headers=auth_headers).json()
        best = data["versions"][0]
        worst = data["versions"][1]
        assert best["response_rate"] > worst["response_rate"]
        assert best["response_rate"] == 0.75
        assert worst["response_rate"] == 0.5

    def test_best_version_is_identified(self, client, auth_headers):
        data = client.get("/api/v1/analytics/resumes", headers=auth_headers).json()
        assert data["best_version"] is not None
        assert data["recommendation"] != ""

    def test_each_version_has_correct_total(self, client, auth_headers):
        data = client.get("/api/v1/analytics/resumes", headers=auth_headers).json()
        for version in data["versions"]:
            assert version["total_sent"] == 4


class TestScoreVsCallback:
    def test_returns_10_buckets(self, client, auth_headers):
        data = client.get("/api/v1/analytics/score-callback", headers=auth_headers).json()
        assert len(data["buckets"]) == 10

    def test_buckets_cover_full_range(self, client, auth_headers):
        data = client.get("/api/v1/analytics/score-callback", headers=auth_headers).json()
        labels = [b["range_label"] for b in data["buckets"]]
        assert "0-10%" in labels
        assert "90-100%" in labels

    def test_high_scores_have_higher_callback(self, client, auth_headers):
        data = client.get("/api/v1/analytics/score-callback", headers=auth_headers).json()
        bucket_90 = next(b for b in data["buckets"] if b["range_label"] == "90-100%")
        assert bucket_90["total_applications"] >= 1
        assert bucket_90["response_rate"] > 0

    def test_min_effective_score_exists(self, client, auth_headers):
        data = client.get("/api/v1/analytics/score-callback", headers=auth_headers).json()
        assert data["min_effective_score"] is not None
        assert data["min_effective_score"] <= 0.75

    def test_sweet_spot_message(self, client, auth_headers):
        data = client.get("/api/v1/analytics/score-callback", headers=auth_headers).json()
        assert len(data["sweet_spot"]) > 0


class TestTrends:
    def test_weekly_trends(self, client, auth_headers):
        data = client.get("/api/v1/analytics/trends?period=weekly", headers=auth_headers).json()
        assert data["period_type"] == "weekly"
        assert data["total_periods"] > 0

    def test_monthly_trends(self, client, auth_headers):
        data = client.get("/api/v1/analytics/trends?period=monthly", headers=auth_headers).json()
        assert data["period_type"] == "monthly"
        assert data["total_periods"] == 2

    def test_trend_points_have_correct_structure(self, client, auth_headers):
        data = client.get("/api/v1/analytics/trends?period=monthly", headers=auth_headers).json()
        for point in data["data_points"]:
            assert "period" in point
            assert "applications" in point
            assert point["applications"] > 0

    def test_monthly_totals_add_up(self, client, auth_headers):
        data = client.get("/api/v1/analytics/trends?period=monthly", headers=auth_headers).json()
        total_apps = sum(p["applications"] for p in data["data_points"])
        assert total_apps == 10

    def test_invalid_period_returns_422(self, client, auth_headers):
        response = client.get("/api/v1/analytics/trends?period=daily", headers=auth_headers)
        assert response.status_code == 422