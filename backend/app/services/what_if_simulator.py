from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.hr_entities import Employee, AttendanceRecord
from backend.app.services.attrition_model import attrition_service

class WhatIfSimulationEngine:
    """Simulates the impact of workforce parameter adjustments on projected attrition risk and department retention."""

    AVG_TURNOVER_REPLACEMENT_COST = 45000.0  # Industry standard replacement cost per departing employee

    def simulate_policy_adjustment(
        self,
        db: Session,
        department_name: str = "Engineering",
        overtime_delta_pct: float = -25.0,  # e.g. -25%
        salary_delta_pct: float = 0.0,       # e.g. +5% or +10%
        promotion_acceleration_months: int = 0,
        added_headcount: int = 0
    ) -> Dict[str, Any]:
        # Fetch target department employees
        query = db.query(Employee).filter(Employee.status == "Active")
        if department_name and department_name.lower() != "all":
            query = query.filter(Employee.department_name == department_name)
        employees = query.all()

        if not employees:
            return {
                "error": f"No active employees found for department: {department_name}",
                "disclaimer": "Model-based projection, not a guaranteed outcome."
            }

        baseline_risks = []
        simulated_risks = []
        total_overtime_baseline = 0.0
        total_overtime_simulated = 0.0
        total_payroll_baseline = 0.0
        total_payroll_simulated = 0.0

        for emp in employees:
            # Get latest attendance
            att = db.query(AttendanceRecord).filter(AttendanceRecord.emp_id == emp.id).order_by(AttendanceRecord.id.desc()).first()
            ot = att.overtime_hours if att else 5.0
            absent_rate = (att.days_absent / max(1, att.working_days)) if att else 0.05

            emp_data_base = {
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

            pred_base = attrition_service.predict_employee_risk(emp_data_base)
            baseline_risks.append(pred_base["attrition_probability"])

            # Compute Simulated Parameters
            # Additional headcount absorbs overtime proportionally
            capacity_boost = 1.0 - (added_headcount / max(1, len(employees) + added_headcount))
            sim_ot = max(0.0, ot * (1.0 + overtime_delta_pct / 100.0) * capacity_boost)
            sim_salary = emp.current_salary * (1.0 + salary_delta_pct / 100.0)
            sim_promo = max(0, emp.months_since_last_promotion - promotion_acceleration_months)
            sim_pulse = min(10.0, emp.pulse_satisfaction_score + (0.5 if salary_delta_pct > 0 else 0) + (0.4 if overtime_delta_pct < -15 else 0))

            emp_data_sim = dict(emp_data_base)
            emp_data_sim["overtime_monthly_avg"] = sim_ot
            emp_data_sim["salary"] = sim_salary
            emp_data_sim["months_since_last_promotion"] = sim_promo
            emp_data_sim["pulse_satisfaction_score"] = sim_pulse

            pred_sim = attrition_service.predict_employee_risk(emp_data_sim)
            simulated_risks.append(pred_sim["attrition_probability"])

            total_overtime_baseline += ot
            total_overtime_simulated += sim_ot
            total_payroll_baseline += emp.current_salary
            total_payroll_simulated += sim_salary

        headcount = len(employees)
        current_avg_risk = float(sum(baseline_risks) / max(1, headcount))
        projected_avg_risk = float(sum(simulated_risks) / max(1, headcount))
        improvement_pp = round((current_avg_risk - projected_avg_risk) * 100.0, 2)

        # Financial ROI Modeling
        annual_payroll_delta = total_payroll_simulated - total_payroll_baseline
        estimated_departures_baseline = current_avg_risk * headcount
        estimated_departures_simulated = projected_avg_risk * headcount
        departures_prevented = max(0.0, estimated_departures_baseline - estimated_departures_simulated)
        estimated_turnover_savings = departures_prevented * self.AVG_TURNOVER_REPLACEMENT_COST
        net_financial_roi = estimated_turnover_savings - annual_payroll_delta

        return {
            "department": department_name,
            "cohort_headcount": headcount,
            "simulated_parameters": {
                "overtime_adjustment_pct": f"{overtime_delta_pct:+.1f}%",
                "salary_adjustment_pct": f"{salary_delta_pct:+.1f}%",
                "promotion_acceleration_months": promotion_acceleration_months,
                "added_headcount": added_headcount
            },
            "current_state": {
                "attrition_risk_pct": round(current_avg_risk * 100.0, 1),
                "avg_overtime_hrs_per_emp": round(total_overtime_baseline / max(1, headcount), 1),
                "annual_payroll_usd": round(total_payroll_baseline, 0),
                "projected_departures": round(estimated_departures_baseline, 1)
            },
            "projected_state": {
                "attrition_risk_pct": round(projected_avg_risk * 100.0, 1),
                "avg_overtime_hrs_per_emp": round(total_overtime_simulated / max(1, headcount), 1),
                "annual_payroll_usd": round(total_payroll_simulated, 0),
                "projected_departures": round(estimated_departures_simulated, 1)
            },
            "impact_analysis": {
                "estimated_improvement_pp": improvement_pp,
                "departures_prevented_annually": round(departures_prevented, 1),
                "turnover_replacement_savings_usd": round(estimated_turnover_savings, 0),
                "net_annual_financial_benefit_usd": round(net_financial_roi, 0)
            },
            "model_disclaimer": "Model-based projection, not a guaranteed outcome. Estimates are derived from calibrated neural network feature sensitivity."
        }

what_if_engine = WhatIfSimulationEngine()
