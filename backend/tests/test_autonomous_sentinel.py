import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.services.sentinel_daemon import sentinel_daemon

client = TestClient(app)

def test_sentinel_daemon_tick():
    """Verify the autonomous sentinel daemon executes a tick evaluating core operational HRM functions."""
    tick_result = sentinel_daemon.execute_tick()
    assert tick_result is not None
    assert tick_result["tick_number"] >= 1
    assert "timestamp" in tick_result
    assert isinstance(tick_result["findings"], list)
    assert len(tick_result["findings"]) >= 3

def test_executive_briefing_endpoint():
    """Verify the Executive Morning Briefing endpoint returns core 7-function health and financial impact."""
    response = client.get("/api/v1/agent/briefing")
    assert response.status_code == 200
    data = response.json()
    assert data["agent_name"] == "Atlas"
    assert "24/7 Autonomous People Operations Partner" in data["tagline"]
    assert "operating_mode" in data
    assert data["financial_savings_secured_usd"] > 0
    assert len(data["cherrington_functions"]) == 7
    assert len(data["marthalia_benefits"]) == 5
    assert len(data["strategic_recommendations"]) > 0

def test_personnel_research_endpoint():
    """Verify the Personnel Research & Absenteeism analysis endpoint."""
    response = client.get("/api/v1/agent/sentinel/research")
    assert response.status_code == 200
    data = response.json()
    assert "Workforce Intelligence" in data["academic_foundation"]
    assert "absenteeism_analysis" in data
    assert data["absenteeism_analysis"]["overall_absence_rate_pct"] > 0
    assert len(data["absenteeism_analysis"]["root_causes"]) >= 2
    assert "recruitment_reasonableness_audit" in data
    assert "workforce_dissatisfaction_matrix" in data

def test_automated_it_provisioning_endpoint():
    """Verify autonomous end-to-end IT onboarding and corporate mail creation."""
    payload = {
        "candidate_name": "Tariq Vance",
        "role_title": "Senior Infrastructure Architect",
        "department": "Engineering",
        "personal_email": "tariq.vance@example.com"
    }
    response = client.post("/api/v1/agent/onboard-new-hire", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["employee_name"] == "Tariq Vance"
    assert data["corporate_email"] == "tariq.vance@worksight.ai"
    assert "Welcome2026!Tariq" in data["temporary_password"]
    assert len(data["it_provisioning"]) == 6
    assert "Apple MacBook Pro 16-inch" in data["hardware_and_stipend"]["primary_laptop"]
    assert data["hardware_and_stipend"]["home_office_stipend_usd"] == 1200.0
    assert data["assigned_buddy"] is not None
    assert data["audit_trail_recorded"] is True

def test_agent_message_briefing_intent():
    """Verify natural language request for executive morning briefing."""
    payload = {
        "sender": "VP of People Operations",
        "message": "Good morning Atlas, what did you do overnight? Give me the executive briefing.",
        "channel": "Slack"
    }
    response = client.post("/api/v1/agent/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "Executive Morning Briefing"
    assert "Core Operations Status" in data["agent_response"]
    assert "Financial Impact" in data["agent_response"]

def test_agent_message_research_intent():
    """Verify natural language request for personnel research."""
    payload = {
        "sender": "CEO",
        "message": "What does our personnel research say about causes of employee absenteeism and delays?",
        "channel": "Web Console"
    }
    response = client.post("/api/v1/agent/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "Personnel Research Analysis"
    assert "attendance analytics" in data["agent_response"]
    assert "Overtime Burnout Fatigue" in data["agent_response"]
