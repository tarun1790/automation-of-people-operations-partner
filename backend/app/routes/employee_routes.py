from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.hr_entities import (
    Employee, AttendanceRecord, PerformanceReview,
    OnboardingJourney, OnboardingTask
)
from backend.app.services.attrition_model import attrition_service
from backend.app.services.performance_intel import performance_intel_service
from backend.app.services.skill_graph import skill_graph_service
from backend.app.services.onboarding_agent import onboarding_agent

router = APIRouter(prefix="/workforce", tags=["Workforce & Employee Intelligence"])

class MobilityPathRequest(BaseModel):
    employee_id: int
    target_role: str

class TaskToggleRequest(BaseModel):
    task_id: int
    is_completed: bool

@router.get("/employees")
def list_employees(
    department: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    query = db.query(Employee).filter(Employee.status == "Active")
    if department:
        query = query.filter(Employee.department_name == department)
    emps = query.all()

    results = []
    for e in emps:
        compa = round(e.current_salary / max(1.0, e.market_salary_benchmark), 2)
        results.append({
            "id": e.id,
            "emp_code": e.emp_code,
            "name": f"{e.first_name} {e.last_name}",
            "email": e.email,
            "department": e.department_name,
            "role_title": e.role_title,
            "seniority_level": e.seniority_level,
            "tenure_months": e.tenure_months,
            "salary": e.current_salary,
            "market_benchmark": e.market_salary_benchmark,
            "compa_ratio": compa,
            "performance_rating": e.performance_rating,
            "pulse_score": e.pulse_satisfaction_score,
            "manager_name": e.manager_name
        })
    return results

@router.get("/attrition-predictions")
def get_workforce_attrition_predictions(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Predicts workforce flight risks using PyTorch CUDA deep neural network with SHAP explainability."""
    employees = db.query(Employee).filter(Employee.status == "Active").all()
    predictions = []

    for emp in employees:
        att = db.query(AttendanceRecord).filter(AttendanceRecord.emp_id == emp.id).order_by(AttendanceRecord.id.desc()).first()
        ot = att.overtime_hours if att else 5.0
        absent_rate = (att.days_absent / max(1, att.working_days)) if att else 0.05

        emp_payload = {
            "id": emp.id,
            "emp_code": emp.emp_code,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "department_name": emp.department_name,
            "role_title": emp.role_title,
            "tenure_months": emp.tenure_months,
            "salary": emp.current_salary,
            "market_salary_benchmark": emp.market_salary_benchmark,
            "performance_rating": emp.performance_rating,
            "potential_rating": emp.potential_rating,
            "months_since_last_promotion": emp.months_since_last_promotion,
            "overtime_monthly_avg": ot,
            "absenteeism_rate": absent_rate,
            "tardiness_count": att.tardiness_count if att else 0,
            "pulse_satisfaction_score": emp.pulse_satisfaction_score,
            "commute_distance_km": emp.commute_distance_km,
            "remote_work_ratio": emp.remote_work_ratio,
            "recognition_count": emp.recognition_count
        }
        res = attrition_service.predict_employee_risk(emp_payload)
        predictions.append(res)

    # Sort descending by risk score
    predictions.sort(key=lambda x: x["attrition_probability"], reverse=True)
    return predictions

@router.get("/performance-matrix")
def get_performance_intelligence(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Generates 9-Box talent matrix distribution, OKR progress, and promotion readiness scoring."""
    return performance_intel_service.evaluate_workforce_performance(db)

@router.get("/skills-graph")
def get_workforce_skills_graph(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Returns NetworkX skill graph topology, SPOFs, and department skill coverage."""
    return skill_graph_service.get_graph_data(db)

@router.post("/mobility-path")
def calculate_internal_mobility_path(
    request: MobilityPathRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Computes shortest skill gap pathway for internal employee mobility."""
    return skill_graph_service.compute_internal_mobility_path(db, request.employee_id, request.target_role)

@router.get("/onboarding-journeys")
def list_onboarding_journeys(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    journeys = db.query(OnboardingJourney).all()
    results = []
    for j in journeys:
        emp = db.query(Employee).filter(Employee.id == j.emp_id).first()
        tasks = db.query(OnboardingTask).filter(OnboardingTask.journey_id == j.id).all()
        completed_count = sum(1 for t in tasks if t.is_completed)
        progress = round((completed_count / max(1, len(tasks))) * 100.0, 1)

        pacing = onboarding_agent.assess_pacing_status(j.current_day, len(tasks), completed_count)

        results.append({
            "id": j.id,
            "emp_id": j.emp_id,
            "employee_name": f"{emp.first_name} {emp.last_name}" if emp else "Employee",
            "department": j.department,
            "role_title": j.role_title,
            "cohort": j.cohort,
            "start_date": j.start_date,
            "current_day": j.current_day,
            "progress_pct": progress,
            "status": pacing,
            "assigned_buddy": j.assigned_buddy,
            "hr_mentor": j.hr_mentor,
            "adaptive_notes": j.adaptive_notes,
            "tasks": [{
                "id": t.id,
                "milestone_phase": t.milestone_phase,
                "category": t.category,
                "task_name": t.task_name,
                "description": t.description,
                "is_completed": t.is_completed,
                "completed_date": t.completed_date
            } for t in tasks]
        })
    return results

@router.post("/onboarding/task-toggle")
def toggle_onboarding_task(
    request: TaskToggleRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    task = db.query(OnboardingTask).filter(OnboardingTask.id == request.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_completed = request.is_completed
    db.commit()
    return {"success": True, "task_id": task.id, "is_completed": task.is_completed}
