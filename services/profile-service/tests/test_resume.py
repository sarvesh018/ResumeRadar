import io


class TestResumeUpload:
    def test_upload_rejects_unsupported_file_type(self, client, auth_headers):
        """Uploading a .exe should be rejected."""
        fake_file = io.BytesIO(b"fake content")
        response = client.post(
            "/api/v1/resumes/upload",
            headers=auth_headers,
            files={"file": ("malware.exe", fake_file, "application/octet-stream")},
            data={"version_name": "test"},
        )
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["title"]

    def test_upload_rejects_missing_version_name(self, client, auth_headers):
        """version_name is required."""
        fake_file = io.BytesIO(b"fake content")
        response = client.post(
            "/api/v1/resumes/upload",
            headers=auth_headers,
            files={"file": ("resume.pdf", fake_file, "application/pdf")},
        )
        assert response.status_code == 422

    def test_upload_pdf_creates_resume_record(self, client, auth_headers):
        """Uploading a valid PDF creates a resume record in the DB."""
        fake_pdf = io.BytesIO(b"%PDF-1.4 fake content")
        response = client.post(
            "/api/v1/resumes/upload",
            headers=auth_headers,
            files={"file": ("resume.pdf", fake_pdf, "application/pdf")},
            data={"version_name": "DevOps v1"},
        )
        assert response.status_code == 201

        data = response.json()
        assert data["resume"]["version_name"] == "DevOps v1"
        assert data["resume"]["file_type"] == "pdf"
        assert data["message"] == "Resume uploaded and parsed successfully"

    def test_upload_docx_creates_resume_record(self, client, auth_headers):
        """DOCX uploads should also be accepted."""
        fake_docx = io.BytesIO(b"PK fake docx content")
        response = client.post(
            "/api/v1/resumes/upload",
            headers=auth_headers,
            files={"file": ("resume.docx", fake_docx, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={"version_name": "Backend v1"},
        )
        assert response.status_code == 201
        assert response.json()["resume"]["file_type"] == "docx"

    def test_upload_without_auth_returns_401(self, client):
        """No token -> 401."""
        fake_file = io.BytesIO(b"content")
        response = client.post(
            "/api/v1/resumes/upload",
            files={"file": ("resume.pdf", fake_file, "application/pdf")},
            data={"version_name": "test"},
        )
        assert response.status_code == 401


class TestResumeList:
    def _upload_resume(self, client, auth_headers, name="Test v1"):
        """Helper to upload a resume."""
        fake_pdf = io.BytesIO(b"%PDF-1.4 fake")
        client.post(
            "/api/v1/resumes/upload",
            headers=auth_headers,
            files={"file": ("resume.pdf", fake_pdf, "application/pdf")},
            data={"version_name": name},
        )

    def test_list_resumes_empty(self, client, auth_headers):
        """No resumes uploaded yet -> empty list."""
        response = client.get("/api/v1/resumes", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 0
        assert response.json()["resumes"] == []

    def test_list_resumes_after_upload(self, client, auth_headers):
        """Upload two resumes -> list shows both."""
        self._upload_resume(client, auth_headers, "Version A")
        self._upload_resume(client, auth_headers, "Version B")

        response = client.get("/api/v1/resumes", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 2


class TestResumeDelete:
    def test_delete_resume(self, client, auth_headers):
        """Delete a resume -> it disappears from the list."""
        fake_pdf = io.BytesIO(b"%PDF-1.4 fake")
        upload_response = client.post(
            "/api/v1/resumes/upload",
            headers=auth_headers,
            files={"file": ("resume.pdf", fake_pdf, "application/pdf")},
            data={"version_name": "To Delete"},
        )
        resume_id = upload_response.json()["resume"]["id"]

        delete_response = client.delete(
            f"/api/v1/resumes/{resume_id}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 200

        get_response = client.get(
            f"/api/v1/resumes/{resume_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_delete_nonexistent_resume_returns_404(self, client, auth_headers):
        """Deleting a non-existent resume -> 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(
            f"/api/v1/resumes/{fake_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404