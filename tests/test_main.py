import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "resume-analyzer-api"}

def test_analyze_resume_invalid_format():
    # Attempting to upload a non-PDF file should trigger 400 Bad Request
    response = client.post(
        "/api/v1/analyze-resume",
        files={"file": ("resume.txt", b"some plain text", "text/plain")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file format. Only PDF files are supported."