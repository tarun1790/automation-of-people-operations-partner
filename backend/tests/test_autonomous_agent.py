import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.services.autonomous_agent import autonomous_agent

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_autonomous_agent_status_and_mode():
    status = autonomous_agent.get_status()
    assert "mode" in status
    assert "status" in status
    assert "total_savings_secured_usd" in status
    assert status["mode"] in ["Autonomous", "Supervised"]

    # Test mode toggle
    res_sup = autonomous_agent.set_mode("Supervised")
    assert res_sup["success"] is True
    assert autonomous_agent.mode == "Supervised"

    res_auto = autonomous_agent.set_mode("Autonomous")
    assert res_auto["success"] is True
    assert autonomous_agent.mode == "Autonomous"

def test_autonomous_patrol(db_session):
    patrol_result = autonomous_agent.run_autonomous_patrol(db_session)
    assert patrol_result["employees_scanned"] == 32
    assert "critical_findings_count" in patrol_result
    assert "actions_executed" in patrol_result
    assert isinstance(patrol_result["actions_executed"], list)
    assert patrol_result["total_savings_secured_usd"] >= 0

def test_process_incoming_message_retention(db_session):
    msg = "Elena Rostova is logging high overtime and seems burnt out. Rebalance her schedule and prepare retention package."
    res = autonomous_agent.process_incoming_message(
        db=db_session,
        sender="David Vance (VP Engineering)",
        message_text=msg,
        channel="Slack #hr-leadership"
    )
    assert res["intent"] == "Retention Risk Mitigation"
    assert "Elena" in res["agent_response"] or "78.4%" in res["agent_response"] or "simulation" in res["agent_response"]
    assert len(res["actions_taken"]) > 0
    assert res["simulation_result"] is not None

def test_process_incoming_message_recruitment(db_session):
    msg = "Screen applicant resumes for open roles using blind screening."
    res = autonomous_agent.process_incoming_message(
        db=db_session,
        sender="Recruitment Lead",
        message_text=msg
    )
    assert res["intent"] == "Autonomous Candidate Screening"
    assert "REQ-2025-01" in res["agent_response"] or "candidates" in res["agent_response"]

def test_process_incoming_message_policy(db_session):
    msg = "What is the parental leave duration?"
    res = autonomous_agent.process_incoming_message(
        db=db_session,
        sender="Marcus Brody",
        message_text=msg
    )
    assert res["intent"] == "Policy Handbook Guidance"
    assert "weeks" in res["agent_response"].lower() or "leave" in res["agent_response"].lower()

def test_agent_api_endpoints(client):
    # Test GET /api/v1/agent/status
    res = client.get("/api/v1/agent/status")
    assert res.status_code == 200
    data = res.json()
    assert "mode" in data
    assert "total_messages_processed" in data

    # Test POST /api/v1/agent/mode
    res_mode = client.post("/api/v1/agent/mode", json={"mode": "Autonomous"})
    assert res_mode.status_code == 200
    assert res_mode.json()["current_mode"] == "Autonomous"

    # Test POST /api/v1/agent/patrol
    res_patrol = client.post("/api/v1/agent/patrol")
    assert res_patrol.status_code == 200
    assert "actions_executed" in res_patrol.json()

    # Test POST /api/v1/agent/message
    res_msg = client.post("/api/v1/agent/message", json={
        "sender": "CEO Office",
        "message": "Run a full audit of all departments and report critical flight risks.",
        "channel": "Email"
    })
    assert res_msg.status_code == 200
    msg_data = res_msg.json()
    assert "agent_response" in msg_data
    assert msg_data["intent"] == "Autonomous Organization Patrol"

    # Test GET /api/v1/agent/feed
    res_feed = client.get("/api/v1/agent/feed")
    assert res_feed.status_code == 200
    feed = res_feed.json()
    assert isinstance(feed, list)
    assert len(feed) > 0
