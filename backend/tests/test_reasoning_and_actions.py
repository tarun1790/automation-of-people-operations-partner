import pytest
from backend.app.database import SessionLocal
from backend.app.models.hr_entities import HRAction, AuditLog
from backend.app.services.cross_reasoner import cross_reasoning_engine
from backend.app.services.audit_service import audit_action_service

def test_cross_source_reasoner_synthesis():
    db = SessionLocal()
    try:
        findings = cross_reasoning_engine.perform_cross_source_audit(db)
        assert len(findings) > 0, "Expected cross-source findings"

        # Check critical finding structure
        crit_finding = next((f for f in findings if f["risk_tier"] == "CRITICAL"), None)
        assert crit_finding is not None
        assert "evidence" in crit_finding
        assert len(crit_finding["evidence"]) >= 3
        assert "reasoning" in crit_finding
        assert "recommended_action" in crit_finding
        assert "expected_impact" in crit_finding
        assert crit_finding["confidence"] >= 80.0
    finally:
        db.close()

def test_human_in_the_loop_action_approval():
    db = SessionLocal()
    try:
        action = db.query(HRAction).filter(HRAction.status == "Pending Approval").first()
        if not action:
            # Create dummy action for test
            action = HRAction(
                action_type="Retention Intervention",
                title="Test Approval Action",
                target_entity="Engineering Staff",
                priority="High",
                status="Pending Approval"
            )
            db.add(action)
            db.commit()

        initial_status = action.status
        action_id = action.id

        # Human reviews and approves
        res = audit_action_service.review_action(
            db=db,
            action_id=action_id,
            decision="Approved",
            actor="Sarah Jenkins (HR Director)",
            notes="Approved after board compensation calibration."
        )

        assert res["success"] is True
        assert res["status"] == "Approved"
        assert res["approved_by"] == "Sarah Jenkins (HR Director)"

        # Check Immutable Audit Trail
        latest_audit = db.query(AuditLog).filter(AuditLog.action_id == action_id).order_by(AuditLog.id.desc()).first()
        assert latest_audit is not None
        assert latest_audit.event_type == "HumanDecision"
        assert "Approved" in latest_audit.summary
    finally:
        db.close()

def test_cross_source_reasoning_endpoint():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    client = TestClient(app)
    response = client.get("/api/v1/dashboard/cross-source-reasoning")
    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "Multi-Source Cross-Reasoning Engine"
    assert len(data["data_sources_integrated"]) >= 5
    assert "findings" in data
    assert len(data["findings"]) > 0
