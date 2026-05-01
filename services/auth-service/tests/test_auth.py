class TestHealthCheck:
    def test_liveness_returns_200(self, client):
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"


class TestRegistration:
    def test_register_new_user_returns_201(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["full_name"] == "Test User"
        assert data["user"]["is_active"] is True
        assert data["user"]["is_verified"] is False
        assert "password_hash" not in data["user"]
        assert "password" not in data["user"]

    def test_register_with_existing_email_returns_409(self, client):
        payload = {"email": "dupe@example.com", "password": "password123"}
        response1 = client.post("/api/v1/auth/register", json=payload)
        assert response1.status_code == 201
        response2 = client.post("/api/v1/auth/register", json=payload)
        assert response2.status_code == 409

    def test_register_with_short_password_returns_422(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "short@example.com",
            "password": "short",
        })
        assert response.status_code == 422

    def test_register_with_invalid_email_returns_422(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "password123",
        })
        assert response.status_code == 422

    def test_register_without_full_name_succeeds(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "noname@example.com",
            "password": "password123",
        })
        assert response.status_code == 201
        assert response.json()["user"]["full_name"] is None


class TestLogin:
    def _register_user(self, client, email="login@example.com", password="password123"):
        client.post("/api/v1/auth/register", json={"email": email, "password": password})

    def test_login_with_valid_credentials_returns_tokens(self, client):
        self._register_user(client)
        response = client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "password123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    def test_login_with_wrong_password_returns_401(self, client):
        self._register_user(client)
        response = client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["title"]

    def test_login_with_unknown_email_returns_401(self, client):
        response = client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "password123",
        })
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["title"]


class TestGetMe:
    def _get_token(self, client) -> str:
        client.post("/api/v1/auth/register", json={
            "email": "me@example.com",
            "password": "password123",
            "full_name": "Me User",
        })
        login_response = client.post("/api/v1/auth/login", json={
            "email": "me@example.com",
            "password": "password123",
        })
        return login_response.json()["access_token"]

    def test_get_me_with_valid_token(self, client):
        token = self._get_token(client)
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        assert data["full_name"] == "Me User"

    def test_get_me_without_token_returns_401(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_get_me_with_invalid_token_returns_401(self, client):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401