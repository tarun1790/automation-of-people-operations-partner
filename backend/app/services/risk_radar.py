from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.hr_entities import (
    Employee, Department, AttendanceRecord, PerformanceReview,
    EmployeeSkill, OnboardingJourney, JobPosting
)

class WorkforceRiskRadar:
    """Early warning system monitoring multi-signal anomalies across departments."""

    def scan_organization_risks(self, db: Session) -> Dict[str, Any]:
        departments = db.query(Department).all()
        dept_risk_cards = []
        org_wide_alerts = []

        total_employees = db.query(Employee).filter(Employee.status == "Active").count()

        for dept in departments:
            emps = db.query(Employee).filter(
                Employee.department_name == dept.name,
                Employee.status == "Active"
            ).all()

            if not emps:
                continue

            emp_ids = [e.id for e in emps]
            headcount = len(emps)

            # 1. Overtime & Absenteeism Signals
            attendances = db.query(AttendanceRecord).filter(AttendanceRecord.emp_id.in_(emp_ids)).all()
            total_ot = sum(a.overtime_hours for a in attendances) if attendances else 0.0
            avg_ot = total_ot / max(1, len(attendances))
            total_absences = sum(a.days_absent for a in attendances) if attendances else 0
            avg_absenteeism_pct = (total_absences / max(1, sum(a.working_days for a in attendances))) * 100.0 if attendances else 2.0

            # 2. Compensation Disparity Signal
            comp_gaps = [e.market_salary_benchmark - e.current_salary for e in emps if e.current_salary < e.market_salary_benchmark]
            below_market_ratio = len(comp_gaps) / max(1, headcount)

            # 3. Performance & Sentiment Trajectory
            avg_pulse = sum(e.pulse_satisfaction_score for e in emps) / max(1, headcount)
            avg_perf = sum(e.performance_rating for e in emps) / max(1, headcount)

            # 4. Critical Skill Bottleneck
            skills = db.query(EmployeeSkill).filter(EmployeeSkill.emp_id.in_(emp_ids)).all()
            unique_skills = set(s.skill_name for s in skills)
            critical_spofs = []
            for sk_name in unique_skills:
                count = sum(1 for s in skills if s.skill_name == sk_name)
                if count == 1:
                    critical_spofs.append(sk_name)

            # 5. Onboarding Stagnation
            journeys = db.query(OnboardingJourney).filter(OnboardingJourney.emp_id.in_(emp_ids)).all()
            at_risk_onboarding = sum(1 for j in journeys if j.status == "AtRisk")

            # Detect Anomaly Signals
            detected_signals = []
            risk_points = 0

            if avg_ot > 15.0:
                detected_signals.append(f"Excessive overtime detected: {avg_ot:.1f} hrs/month per employee (+{int(avg_ot * 1.8)}% vs safe norm)")
                risk_points += 3
            elif avg_ot > 10.0:
                detected_signals.append(f"Moderate overtime accumulation: {avg_ot:.1f} hrs/mo")
                risk_points += 1

            if below_market_ratio >= 0.40:
                detected_signals.append(f"Compensation disparity: {int(below_market_ratio * 100)}% of team compensated below peer market median")
                risk_points += 3

            if avg_pulse < 6.0:
                detected_signals.append(f"Depressed pulse sentiment: {avg_pulse:.1f}/10 indicates employee fatigue or disengagement")
                risk_points += 2

            if avg_absenteeism_pct > 8.0:
                detected_signals.append(f"Unplanned absenteeism spike: {avg_absenteeism_pct:.1f}% monthly absence rate")
                risk_points += 2

            if critical_spofs:
                detected_signals.append(f"Critical single-point-of-failure skills: {', '.join(critical_spofs[:3])}")
                risk_points += 2

            if at_risk_onboarding > 0:
                detected_signals.append(f"{at_risk_onboarding} new hire onboarding journeys currently flagged as At-Risk")
                risk_points += 1

            # Determine Department Risk Tier
            if risk_points >= 6:
                tier = "CRITICAL"
                recommended_action = "Initiate immediate workload redistribution, spot retention compensation reviews, and leadership 1-on-1s."
            elif risk_points >= 4:
                tier = "HIGH"
                recommended_action = "Conduct manager workload audit, cross-train for single-point skills, and review compensation benchmarks."
            elif risk_points >= 2:
                tier = "MODERATE"
                recommended_action = "Monitor pulse survey cadence and provide targeted mentorship."
            else:
                tier = "LOW"
                recommended_action = "Workforce metrics healthy and within standard operating tolerance."

            card = {
                "department": dept.name,
                "headcount": headcount,
                "risk_level": tier,
                "risk_score": min(100, risk_points * 12 + 10),
                "detected_signals": detected_signals,
                "priority": "CRITICAL" if tier == "CRITICAL" else "HIGH" if tier == "HIGH" else "NORMAL",
                "metrics": {
                    "avg_overtime_hrs": round(avg_ot, 1),
                    "absenteeism_pct": round(avg_absenteeism_pct, 1),
                    "avg_pulse_score": round(avg_pulse, 1),
                    "below_market_pct": round(below_market_ratio * 100.0, 1),
                    "critical_spofs_count": len(critical_spofs)
                },
                "recommended_action": recommended_action
            }
            dept_risk_cards.append(card)

            if tier in ["CRITICAL", "HIGH"]:
                org_wide_alerts.append({
                    "department": dept.name,
                    "level": tier,
                    "summary": f"{dept.name} department risk level elevated ({tier}). Signals: {len(detected_signals)} active risk indicators.",
                    "primary_driver": detected_signals[0] if detected_signals else "Operational friction"
                })

        # Sort department cards by risk score descending
        dept_risk_cards.sort(key=lambda x: x["risk_score"], reverse=True)

        return {
            "monitored_departments_count": len(dept_risk_cards),
            "total_workforce_headcount": total_employees,
            "critical_risk_departments": sum(1 for c in dept_risk_cards if c["risk_level"] == "CRITICAL"),
            "high_risk_departments": sum(1 for c in dept_risk_cards if c["risk_level"] == "HIGH"),
            "active_radar_alerts": org_wide_alerts,
            "department_risk_matrix": dept_risk_cards
        }

risk_radar_service = WorkforceRiskRadar()
