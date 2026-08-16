import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_cvs"))

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_dashboard_stats_endpoint():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_cvs" in data
    assert "strong_matches" in data

def test_domains_list_endpoint():
    response = client.get("/api/domains")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 12

def test_upload_and_processing_flow():
    txt_path = os.path.join(SAMPLE_DIR, "sample_web_developer.txt")
    if os.path.exists(txt_path):
        with open(txt_path, "rb") as f:
            response = client.post(
                "/api/candidates/upload",
                files={"files": ("sample_web_developer.txt", f, "text/plain")}
            )
        assert response.status_code == 202
        res_data = response.json()
        assert res_data["total_uploaded"] == 1
        cand_id = res_data["results"][0]["candidate_id"]

        # Retrieve candidate detail
        detail_res = client.get(f"/api/candidates/{cand_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["id"] == cand_id
