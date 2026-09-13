import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["hardware_acceleration"]["cuda_available"] is True
    assert "cuda" in data["hardware_acceleration"]["device"]

def test_dashboard_summary_endpoint():
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_employees" in data
    assert data["total_employees"] > 0
    assert "workforce_health_score" in data

def test_what_if_simulation_endpoint():
    payload = {
        "department": "Engineering",
        "overtime_delta_pct": -20.0,
        "salary_delta_pct": 5.0
    }
    response = client.post("/api/v1/simulation/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "impact_analysis" in data
    assert "model_disclaimer" in data

def test_policy_rag_query_endpoint():
    payload = {"query": "What is the parental leave duration?"}
    response = client.post("/api/v1/policy/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "citations" in data
    assert len(data["citations"]) > 0
    assert "supporting_evidence" in data

def test_natural_language_command_center():
    payload = {"query": "Why is Engineering showing increased attrition?"}
    response = client.post("/api/v1/dashboard/command-center", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "tool_called" in data
    assert "executive_summary" in data
    assert "evidence" in data
