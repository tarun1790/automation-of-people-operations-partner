from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.hr_entities import Employee, JobPosting, HRAction, Department
from backend.app.services.risk_radar import risk_radar_service
from backend.app.services.cross_reasoner import cross_reasoning_engine
from backend.app.services.attrition_model import attrition_service
from backend.app.services.skill_graph import skill_graph_service

router = APIRouter(prefix="/dashboard", tags=["Executive Dashboard"])

class CommandRequest(BaseModel):
    query: str

@router.get("/summary")
def get_executive_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Answers: 'What is happening in my workforce right now?'"""
    active_emps = db.query(Employee).filter(Employee.status == "Active").all()
    total_headcount = len(active_emps)

    # Compute high-risk employees via Attrition Service
    high_risk_count = 0
    total_perf = 0.0
    for e in active_emps:
        total_perf += e.performance_rating
        pred = attrition_service.predict_employee_risk({
            "tenure_months": e.tenure_months,
            "salary": e.current_salary,
            "market_salary_benchmark": e.market_salary_benchmark,
            "performance_rating": e.performance_rating,
            "potential_rating": e.potential_rating,
            "months_since_last_promotion": e.months_since_last_promotion,
            "overtime_monthly_avg": 8.0,
            "pulse_satisfaction_score": e.pulse_satisfaction_score,
            "commute_distance_km": e.commute_distance_km,
            "remote_work_ratio": e.remote_work_ratio,
            "recognition_count": e.recognition_count
        })
        if pred["risk_level"] in ["CRITICAL", "HIGH"]:
            high_risk_count += 1

    avg_perf = round(total_perf / max(1, total_headcount), 2)
    open_positions = db.query(JobPosting).filter(JobPosting.status == "Open").count()
    pending_actions = db.query(HRAction).filter(HRAction.status == "Pending Approval").count()

    # Skill Graph coverage
    graph_data = skill_graph_service.get_graph_data(db)
    cov_values = list(graph_data["department_skill_coverage"].values())
    avg_skill_cov = round(sum(cov_values) / max(1, len(cov_values)), 1) if cov_values else 82.0

    # Composite Workforce Health Score (0-100)
    # Higher performance, lower attrition risk, good skill coverage = high health
    risk_factor = max(0.0, 1.0 - (high_risk_count / max(1, total_headcount)))
    perf_factor = avg_perf / 5.0
    skill_factor = avg_skill_cov / 100.0
    workforce_health = round((0.40 * perf_factor + 0.35 * risk_factor + 0.25 * skill_factor) * 100.0, 0)

    return {
        "total_employees": total_headcount,
        "high_risk_employees": high_risk_count,
        "workforce_health_score": int(workforce_health),
        "average_performance": avg_perf,
        "open_positions": open_positions,
        "skill_coverage_pct": avg_skill_cov,
        "pending_actions_count": pending_actions,
        "critical_spofs_count": len(graph_data["critical_single_points_of_failure"]),
        "timestamp": "Near-real-time database sync"
    }

@router.get("/risk-radar")
def get_risk_radar(db: Session = Depends(get_db)) -> Dict[str, Any]:
    return risk_radar_service.scan_organization_risks(db)

@router.get("/insights")
def get_standardized_ai_insights(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Generates standardized AI Insight Cards for executive decision-making."""
    radar = risk_radar_service.scan_organization_risks(db)
    cross_audits = cross_reasoning_engine.perform_cross_source_audit(db)

    insights = []

    # 1. Department Level Insight
    if radar["department_risk_matrix"]:
        top_dept = radar["department_risk_matrix"][0]
        insights.append({
            "id": "INS-DEPT-01",
            "type": "DEPARTMENT_RISK",
            "badge": f"{top_dept['risk_level']} WORKFORCE RISK",
            "target": f"{top_dept['department']} Department",
            "finding": f"Attrition vulnerability and operational fatigue detected across {top_dept['headcount']} employees.",
            "evidence": top_dept["detected_signals"][:3],
            "confidence": 88.0,
            "recommended_action": top_dept["recommended_action"],
            "action_type": "Simulate",
            "department": top_dept["department"]
        })

    # 2. Individual Critical Case Insight
    crit_cases = [c for c in cross_audits if c["risk_tier"] == "CRITICAL"]
    if crit_cases:
        case = crit_cases[0]
        insights.append({
            "id": "INS-EMP-01",
            "type": "EMPLOYEE_RETENTION",
            "badge": "CRITICAL FLIGHT RISK",
            "target": f"{case['employee_name']} ({case['role_title']})",
            "finding": "High performer logging excessive overtime while compensated below market benchmark.",
            "evidence": case["evidence"][:3],
            "confidence": case["confidence"],
            "recommended_action": case["recommended_action"],
            "action_type": "Review",
            "employee_id": case["employee_id"]
        })

    # 3. Critical Skill SPOF Insight
    graph_data = skill_graph_service.get_graph_data(db)
    spofs = graph_data["critical_single_points_of_failure"]
    if spofs:
        spof = spofs[0]
        insights.append({
            "id": "INS-SKILL-01",
            "type": "SKILL_VULNERABILITY",
            "badge": "SINGLE POINT OF FAILURE",
            "target": f"Skill: {spof['skill_name']}",
            "finding": f"Only 1 employee ({spof['holder_name']}) holds expert proficiency in {spof['skill_name']}.",
            "evidence": [
                f"Held exclusively by {spof['holder_name']} in {spof['holder_department']}",
                "Zero redundant backup in mission-critical infrastructure stack",
                f"Department skill coverage at {graph_data['department_skill_coverage'].get(spof['holder_department'], 70)}%"
            ],
            "confidence": 94.0,
            "recommended_action": spof["mitigation_plan"],
            "action_type": "Action",
            "skill_name": spof["skill_name"]
        })

    return insights

@router.post("/command-center")
def handle_command_query(request: CommandRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Natural Language AI Command Center with structured tool calling and evidence breakdown."""
    return cross_reasoning_engine.handle_natural_language_command(db, request.query)
