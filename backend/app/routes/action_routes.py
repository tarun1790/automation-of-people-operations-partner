from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.audit_service import audit_action_service
from backend.app.services.attrition_model import attrition_service
from backend.app.services.data_quality import data_quality_service
from backend.app.services.fairness_monitor import fairness_monitor_service

router = APIRouter(prefix="/governance", tags=["Action Center & Governance"])

class ReviewActionRequest(BaseModel):
    decision: str  # 'Approved', 'Rejected', 'Modified', 'Executed'
    actor: str = "HR Director"
    notes: Optional[str] = None
    modified_payload: Optional[Dict[str, Any]] = None

@router.get("/actions")
def get_hr_actions(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Fetches all pending and completed HR Action Center items."""
    return audit_action_service.list_actions(db, status_filter=status)

@router.post("/actions/{action_id}/review")
def review_hr_action(
    action_id: int,
    request: ReviewActionRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Human-in-the-loop review, approval, modification, or execution of an HR recommendation."""
    res = audit_action_service.review_action(
        db=db,
        action_id=action_id,
        decision=request.decision,
        actor=request.actor,
        notes=request.notes,
        modified_payload=request.modified_payload
    )
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.get("/audit-trail")
def get_audit_trail(
    limit: int = 50,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Retrieves immutable decision audit log with full event traceability."""
    return audit_action_service.get_audit_trail(db, limit=limit)

@router.get("/mlops-telemetry")
def get_model_telemetry() -> Dict[str, Any]:
    """Returns MLOps monitoring metrics, calibration, ROC-AUC, and latency telemetry."""
    return attrition_service.get_model_telemetry()

@router.get("/data-quality")
def get_data_quality_report(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Runs real-time schema, missing value, range, and outlier validation checks."""
    return data_quality_service.validate_workforce_data(db)

@router.get("/fairness-monitor")
def get_fairness_audit_report(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Evaluates demographic parity, four-fifths compliance, and adverse impact ratios."""
    return fairness_monitor_service.audit_recruitment_fairness(db)
