import pytest
from backend.app.database import SessionLocal
from backend.app.services.data_quality import data_quality_service
from backend.app.services.fairness_monitor import fairness_monitor_service

def test_data_quality_validation():
    db = SessionLocal()
    try:
        report = data_quality_service.validate_workforce_data(db)
        assert "data_quality_score" in report
        assert report["data_quality_score"] >= 90.0
        assert report["validation_status"] == "Healthy"
        assert "last_validated" in report
    finally:
        db.close()

def test_fairness_and_bias_monitoring():
    db = SessionLocal()
    try:
        audit = fairness_monitor_service.audit_recruitment_fairness(db)
        assert "demographic_parity_score" in audit
        assert "adverse_impact_ratio" in audit
        assert "proxy_audit_results" in audit
        assert len(audit["proxy_audit_results"]) >= 3
    finally:
        db.close()
