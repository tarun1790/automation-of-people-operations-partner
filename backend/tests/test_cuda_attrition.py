import pytest
import torch
from backend.app.config import DEVICE, CUDA_AVAILABLE, GPU_NAME
from backend.app.services.attrition_model import attrition_service

def test_hardware_acceleration_cuda():
    assert CUDA_AVAILABLE is True, "CUDA must be available on RTX 3070 Ti"
    assert "cuda" in str(DEVICE), f"Expected CUDA device, got {DEVICE}"
    assert "3070" in GPU_NAME or "NVIDIA" in GPU_NAME, f"Unexpected GPU: {GPU_NAME}"

def test_attrition_prediction_defensible_phrasing():
    sample_emp = {
        "id": 999,
        "emp_code": "TEST-01",
        "first_name": "Test",
        "last_name": "Engineer",
        "department_name": "Engineering",
        "role_title": "Senior Systems Engineer",
        "tenure_months": 28,
        "salary": 125000,
        "market_salary_benchmark": 160000,
        "performance_rating": 4.6,
        "potential_rating": 3,
        "months_since_last_promotion": 24,
        "overtime_monthly_avg": 34.0,
        "absenteeism_rate": 0.08,
        "tardiness_count": 2,
        "pulse_satisfaction_score": 4.1,
        "commute_distance_km": 20.0,
        "remote_work_ratio": 0.4,
        "recognition_count": 2
    }
    result = attrition_service.predict_employee_risk(sample_emp)

    assert result["risk_level"] in ["CRITICAL", "HIGH"]
    assert "The model estimates elevated attrition risk" in result["defensible_statement"]
    assert "will resign" not in result["defensible_statement"].lower()
    assert len(result["top_contributing_factors"]) > 0
    assert result["confidence"] >= 75.0
    assert result["latency_ms"] >= 0.0
