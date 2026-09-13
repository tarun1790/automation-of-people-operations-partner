from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.what_if_simulator import what_if_engine

router = APIRouter(prefix="/simulation", tags=["What-If Simulator"])

class SimulationRequest(BaseModel):
    department: str = "Engineering"
    overtime_delta_pct: float = -25.0
    salary_delta_pct: float = 0.0
    promotion_acceleration_months: int = 0
    added_headcount: int = 0

@router.post("/simulate")
def run_what_if_scenario(
    request: SimulationRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Simulates the impact of policy and workload interventions using a counterfactual perturbation model."""
    return what_if_engine.simulate_policy_adjustment(
        db=db,
        department_name=request.department,
        overtime_delta_pct=request.overtime_delta_pct,
        salary_delta_pct=request.salary_delta_pct,
        promotion_acceleration_months=request.promotion_acceleration_months,
        added_headcount=request.added_headcount
    )
