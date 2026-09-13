import pytest
from backend.app.database import SessionLocal
from backend.app.services.what_if_simulator import what_if_engine

def test_what_if_counterfactual_simulation():
    db = SessionLocal()
    try:
        res = what_if_engine.simulate_policy_adjustment(
            db=db,
            department_name="Engineering",
            overtime_delta_pct=-25.0,
            salary_delta_pct=5.0
        )
        assert "current_state" in res
        assert "projected_state" in res
        assert "impact_analysis" in res
        assert "Model-based projection, not a guaranteed outcome." in res["model_disclaimer"]

        current_risk = res["current_state"]["attrition_risk_pct"]
        projected_risk = res["projected_state"]["attrition_risk_pct"]
        improvement = res["impact_analysis"]["estimated_improvement_pp"]

        # Risk should decrease when reducing overtime by 25% and increasing salary by 5%
        assert improvement >= 0.0, f"Expected non-negative improvement, got {improvement}"
        assert projected_risk <= current_risk + 0.1
    finally:
        db.close()
