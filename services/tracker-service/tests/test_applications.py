from uuid import uuid4


class TestCreateApplication:
    def test_create_application_returns_201(self, client, auth_headers):
        response = client.post("/api/v1/applications", headers=auth_headers, json={
            "company": "Google", "role_title": "Senior DevOps Engineer",
            "location": "Bangalore", "is_remote": False, "match_score": 0.82,
            "notes": "Referred by a friend",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["company"] == "Google"
        assert data["role_title"] == "Senior DevOps Engineer"
        assert data["status"] == "applied"
        assert data["match_score"] == 0.82
        assert len(data["allowed_transitions"]) > 0

    def test_create_with_wishlist_status(self, client, auth_headers):
        response = client.post("/api/v1/applications", headers=auth_headers, json={
            "company": "Meta", "role_title": "SRE", "status": "wishlist",
        })
        assert response.status_code == 201
        assert response.json()["status"] == "wishlist"

    def test_create_without_auth_returns_401(self, client):
        response = client.post("/api/v1/applications", json={"company": "Test", "role_title": "Test"})
        assert response.status_code == 401

    def test_create_without_required_fields_returns_422(self, client, auth_headers):
        response = client.post("/api/v1/applications", headers=auth_headers, json={})
        assert response.status_code == 422


class TestListApplications:
    def _create_app(self, client, auth_headers, company="TestCorp", status="applied"):
        return client.post("/api/v1/applications", headers=auth_headers, json={
            "company": company, "role_title": "Engineer", "status": status,
        })

    def test_list_empty(self, client, auth_headers):
        response = client.get("/api/v1/applications", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 0

    def test_list_after_creating(self, client, auth_headers):
        self._create_app(client, auth_headers, "CompanyA")
        self._create_app(client, auth_headers, "CompanyB")
        response = client.get("/api/v1/applications", headers=auth_headers)
        assert response.json()["total"] == 2

    def test_list_filter_by_status(self, client, auth_headers):
        self._create_app(client, auth_headers, "Applied Co", "applied")
        self._create_app(client, auth_headers, "Wishlist Co", "wishlist")
        response = client.get("/api/v1/applications?status=wishlist", headers=auth_headers)
        assert response.json()["total"] == 1
        assert response.json()["applications"][0]["company"] == "Wishlist Co"


class TestGetApplication:
    def test_get_by_id_with_status_history(self, client, auth_headers):
        create_resp = client.post("/api/v1/applications", headers=auth_headers, json={
            "company": "Amazon", "role_title": "DevOps",
        })
        app_id = create_resp.json()["id"]
        get_resp = client.get(f"/api/v1/applications/{app_id}", headers=auth_headers)
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["company"] == "Amazon"
        assert len(data["status_events"]) == 1
        assert data["status_events"][0]["to_status"] == "applied"

    def test_get_nonexistent_returns_404(self, client, auth_headers):
        response = client.get(f"/api/v1/applications/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateApplication:
    def test_update_details(self, client, auth_headers):
        create_resp = client.post("/api/v1/applications", headers=auth_headers, json={
            "company": "OldName", "role_title": "Engineer",
        })
        app_id = create_resp.json()["id"]
        update_resp = client.put(f"/api/v1/applications/{app_id}", headers=auth_headers, json={
            "company": "NewName", "notes": "Updated notes",
        })
        assert update_resp.status_code == 200
        assert update_resp.json()["company"] == "NewName"
        assert update_resp.json()["notes"] == "Updated notes"

    def test_update_with_empty_body_returns_400(self, client, auth_headers):
        create_resp = client.post("/api/v1/applications", headers=auth_headers, json={
            "company": "Test", "role_title": "Test",
        })
        app_id = create_resp.json()["id"]
        response = client.put(f"/api/v1/applications/{app_id}", headers=auth_headers, json={})
        assert response.status_code == 400


class TestStatusTransitions:
    def _create_app(self, client, auth_headers):
        resp = client.post("/api/v1/applications", headers=auth_headers, json={
            "company": "TestCorp", "role_title": "DevOps",
        })
        return resp.json()["id"]

    def test_valid_transition_applied_to_screening(self, client, auth_headers):
        app_id = self._create_app(client, auth_headers)
        response = client.patch(f"/api/v1/applications/{app_id}/status", headers=auth_headers,
                                json={"status": "screening", "notes": "Recruiter called"})
        assert response.status_code == 200
        assert response.json()["status"] == "screening"
        assert len(response.json()["status_events"]) == 2
        last_event = response.json()["status_events"][-1]
        assert last_event["from_status"] == "applied"
        assert last_event["to_status"] == "screening"
        assert last_event["notes"] == "Recruiter called"

    def test_valid_transition_to_offer(self, client, auth_headers):
        app_id = self._create_app(client, auth_headers)
        client.patch(f"/api/v1/applications/{app_id}/status", headers=auth_headers, json={"status": "screening"})
        client.patch(f"/api/v1/applications/{app_id}/status", headers=auth_headers, json={"status": "interviewing"})
        response = client.patch(f"/api/v1/applications/{app_id}/status", headers=auth_headers, json={"status": "offer"})
        assert response.status_code == 200
        assert response.json()["status"] == "offer"
        assert len(response.json()["status_events"]) == 4

    def test_invalid_transition_rejected_to_offer(self, client, auth_headers):
        app_id = self._create_app(client, auth_headers)
        client.patch(f"/api/v1/applications/{app_id}/status", headers=auth_headers, json={"status": "rejected"})
        response = client.patch(f"/api/v1/applications/{app_id}/status", headers=auth_headers, json={"status": "offer"})
        assert response.status_code == 400
        assert "Cannot transition" in response.json()["title"]

    def test_invalid_transition_screening_to_applied(self, client, auth_headers):
        app_id = self._create_app(client, auth_headers)
        client.patch(f"/api/v1/applications/{app_id}/status", headers=auth_headers, json={"status": "screening"})
        response = client.patch(f"/api/v1/applications/{app_id}/status", headers=auth_headers, json={"status": "applied"})
        assert response.status_code == 400

    def test_transition_with_response_date(self, client, auth_headers):
        app_id = self._create_app(client, auth_headers)
        response = client.patch(f"/api/v1/applications/{app_id}/status", headers=auth_headers,
                                json={"status": "screening", "response_date": "2024-06-15"})
        assert response.status_code == 200
        assert response.json()["response_date"] == "2024-06-15"

    def test_allowed_transitions_in_response(self, client, auth_headers):
        app_id = self._create_app(client, auth_headers)
        get_resp = client.get(f"/api/v1/applications/{app_id}", headers=auth_headers)
        allowed = get_resp.json()["allowed_transitions"]
        assert "screening" in allowed
        assert "offer" not in allowed


class TestDeleteApplication:
    def test_delete_application(self, client, auth_headers):
        create_resp = client.post("/api/v1/applications", headers=auth_headers, json={
            "company": "ToDelete", "role_title": "Engineer",
        })
        app_id = create_resp.json()["id"]
        delete_resp = client.delete(f"/api/v1/applications/{app_id}", headers=auth_headers)
        assert delete_resp.status_code == 200
        get_resp = client.get(f"/api/v1/applications/{app_id}", headers=auth_headers)
        assert get_resp.status_code == 404

    def test_delete_nonexistent_returns_404(self, client, auth_headers):
        response = client.delete(f"/api/v1/applications/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        assert response.status_code == 404


class TestKanbanBoard:
    def _create_app(self, client, auth_headers, company, status_val="applied"):
        client.post("/api/v1/applications", headers=auth_headers, json={
            "company": company, "role_title": "Engineer", "status": status_val,
        })

    def test_board_shows_all_columns(self, client, auth_headers):
        response = client.get("/api/v1/applications/board", headers=auth_headers)
        assert response.status_code == 200
        statuses = [col["status"] for col in response.json()["columns"]]
        assert "wishlist" in statuses
        assert "applied" in statuses
        assert "offer" in statuses
        assert "rejected" in statuses

    def test_board_groups_correctly(self, client, auth_headers):
        self._create_app(client, auth_headers, "Applied1")
        self._create_app(client, auth_headers, "Applied2")
        self._create_app(client, auth_headers, "Wishlist1", "wishlist")
        response = client.get("/api/v1/applications/board", headers=auth_headers)
        data = response.json()
        assert data["total"] == 3
        applied_col = next(c for c in data["columns"] if c["status"] == "applied")
        wishlist_col = next(c for c in data["columns"] if c["status"] == "wishlist")
        assert applied_col["count"] == 2
        assert wishlist_col["count"] == 1