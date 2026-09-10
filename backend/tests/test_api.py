import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_process_unsupported_file():
    # Test uploading an unsupported file type like a .txt file
    response = client.post(
        "/api/v1/documents/process",
        data={"document_type": "invoice"},
        files={"file": ("test.txt", b"dummy content", "text/plain")}
    )
    assert response.status_code == 400
    json_resp = response.json()
    assert "error" in json_resp
    assert json_resp["error"]["code"] == "UNSUPPORTED_FILE_TYPE"

def test_process_invalid_document_type():
    # Test uploading a valid file type but with invalid document type
    response = client.post(
        "/api/v1/documents/process",
        data={"document_type": "invalid_type"},
        files={"file": ("test.pdf", b"%PDF-1.4 dummy", "application/pdf")}
    )
    assert response.status_code == 400
    assert "Invalid document_type" in response.text
