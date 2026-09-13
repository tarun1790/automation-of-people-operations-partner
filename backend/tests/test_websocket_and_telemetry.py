import pytest
from starlette.testclient import TestClient
from backend.app.main import app

def test_operational_telemetry_endpoint():
    with TestClient(app) as client:
        res = client.get("/api/v1/dashboard/operational-telemetry")
        assert res.status_code == 200
        data = res.json()
        assert "operational_metrics" in data
        metrics = data["operational_metrics"]
        assert "staffing_capacity" in metrics
        assert "performance_fit" in metrics
        assert "compensation_compa" in metrics
        assert "upskilling_rate" in metrics
        assert "relations_pulse" in metrics
        assert "safety_overtime" in metrics
        assert "absence_rate" in metrics
        assert "absenteeism_drivers" in data
        assert "recruitment_audit" in data
        assert "dissatisfaction_analysis" in data

def test_websocket_telemetry_handshake():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/telemetry") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "handshake"
            assert data["status"] == "connected"
            assert "device" in data
            # Send ping
            websocket.send_text("ping")
            reply = websocket.receive_json()
            assert reply["type"] == "pong"
