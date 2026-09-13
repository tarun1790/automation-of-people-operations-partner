import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.hr_entities import HRAction, AuditLog, RecommendationItem

class AuditAndActionService:
    """Manages human-in-the-loop HR Action Center approvals and immutable decision audit logging."""

    def log_event(
        self,
        db: Session,
        event_type: str,
        summary: str,
        actor: str = "System",
        action_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        model_version: str = "WorkSight-CUDA-v2.4"
    ) -> AuditLog:
        log_entry = AuditLog(
            action_id=action_id,
            event_type=event_type,
            model_version=model_version,
            actor=actor,
            summary=summary,
            details_json=json.dumps(details or {}),
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    def review_action(
        self,
        db: Session,
        action_id: int,
        decision: str,  # 'Approved', 'Rejected', 'Modified', 'Executed'
        actor: str = "HR Director",
        notes: Optional[str] = None,
        modified_payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        action = db.query(HRAction).filter(HRAction.id == action_id).first()
        if not action:
            return {"error": f"Action ID #{action_id} not found."}

        prev_status = action.status
        action.status = decision
        action.approved_by = actor
        action.human_notes = notes or action.human_notes
        action.updated_at = datetime.utcnow()

        if decision == "Executed":
            action.outcome_summary = f"Action executed successfully by {actor}. Workflow dispatched to HRIS and line managers."

        db.commit()
        db.refresh(action)

        # Log to Immutable Audit Trail
        audit_details = {
            "action_id": action.id,
            "title": action.title,
            "target_entity": action.target_entity,
            "previous_status": prev_status,
            "new_status": decision,
            "decision_actor": actor,
            "human_notes": notes,
            "modified_payload": modified_payload
        }
        self.log_event(
            db=db,
            event_type="HumanDecision",
            summary=f"{actor} reviewed Action #{action.id}: changed status from '{prev_status}' to '{decision}'.",
            actor=actor,
            action_id=action.id,
            details=audit_details
        )

        return {
            "success": True,
            "action_id": action.id,
            "title": action.title,
            "status": action.status,
            "approved_by": action.approved_by,
            "updated_at": action.updated_at.isoformat(),
            "outcome_summary": action.outcome_summary
        }

    def list_actions(self, db: Session, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        query = db.query(HRAction)
        if status_filter:
            query = query.filter(HRAction.status == status_filter)
        actions = query.order_by(HRAction.created_at.desc()).all()

        results = []
        for a in actions:
            results.append({
                "action_id": a.id,
                "recommendation_id": a.recommendation_id,
                "action_type": a.action_type,
                "title": a.title,
                "target_entity": a.target_entity,
                "reason": a.reason,
                "evidence": a.evidence,
                "priority": a.priority,
                "expected_impact": a.expected_impact,
                "status": a.status,
                "approved_by": a.approved_by,
                "human_notes": a.human_notes,
                "outcome_summary": a.outcome_summary,
                "created_at": a.created_at.strftime("%Y-%m-%d %H:%M") if a.created_at else None,
                "updated_at": a.updated_at.strftime("%Y-%m-%d %H:%M") if a.updated_at else None
            })
        return results

    def get_audit_trail(self, db: Session, limit: int = 50) -> List[Dict[str, Any]]:
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
        results = []
        for l in logs:
            try:
                parsed_details = json.loads(l.details_json) if l.details_json else {}
            except Exception:
                parsed_details = {}
            results.append({
                "id": l.id,
                "action_id": l.action_id,
                "event_type": l.event_type,
                "model_version": l.model_version,
                "actor": l.actor,
                "summary": l.summary,
                "details": parsed_details,
                "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            })
        return results

audit_action_service = AuditAndActionService()
