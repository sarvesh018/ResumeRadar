class TestGetProfile:
    def test_get_profile_auto_creates_if_missing(self, client, auth_headers):
        """First access creates a blank profile automatically."""
        response = client.get("/api/v1/profile", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["user_id"] == auth_headers["_user_id"]
        assert data["full_name"] is None
        assert data["headline"] is None

    def test_get_profile_returns_same_on_second_call(self, client, auth_headers):
        """Second call returns the same profile (not a new one)."""
        response1 = client.get("/api/v1/profile", headers=auth_headers)
        response2 = client.get("/api/v1/profile", headers=auth_headers)

        assert response1.json()["id"] == response2.json()["id"]

    def test_get_profile_without_auth_returns_401(self, client):
        """No token -> 401."""
        response = client.get("/api/v1/profile")
        assert response.status_code == 401


class TestUpdateProfile:
    def test_update_profile_sets_fields(self, client, auth_headers):
        """PUT with fields updates those fields."""
        client.get("/api/v1/profile", headers=auth_headers)

        response = client.put("/api/v1/profile", headers=auth_headers, json={
            "full_name": "John Doe",
            "headline": "Senior DevOps Engineer",
            "years_experience": 3,
            "target_roles": ["DevOps Engineer", "SRE"],
            "linkedin_url": "https://linkedin.com/in/johndoe",
        })
        assert response.status_code == 200

        data = response.json()
        assert data["full_name"] == "John Doe"
        assert data["headline"] == "Senior DevOps Engineer"
        assert data["years_experience"] == 3
        assert data["linkedin_url"] == "https://linkedin.com/in/johndoe"

    def test_partial_update_preserves_other_fields(self, client, auth_headers):
        """Updating one field doesn't wipe others."""
        client.get("/api/v1/profile", headers=auth_headers)
        client.put("/api/v1/profile", headers=auth_headers, json={
            "full_name": "Jane Doe",
            "location": "Pune",
        })

        response = client.put("/api/v1/profile", headers=auth_headers, json={
            "headline": "Cloud Architect",
        })
        assert response.status_code == 200

        data = response.json()
        assert data["full_name"] == "Jane Doe"    # Preserved
        assert data["location"] == "Pune"          # Preserved
        assert data["headline"] == "Cloud Architect"  # Updated

    def test_update_with_empty_body_returns_400(self, client, auth_headers):
        """Sending no fields returns 400."""
        client.get("/api/v1/profile", headers=auth_headers)
        response = client.put("/api/v1/profile", headers=auth_headers, json={})
        assert response.status_code == 400