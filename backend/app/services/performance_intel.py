from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.hr_entities import Employee, PerformanceReview, Feedback360, GoalOKR

class PerformanceIntelligenceService:
    """Evaluates multi-dimensional performance, OKRs, 360 sentiment, and 9-box talent matrix calibration."""

    QUADRANT_LABELS = {
        (3, 3): "High Potential Star",
        (3, 2): "High Performer",
        (3, 1): "Solid Professional",
        (2, 3): "High Potential Growth",
        (2, 2): "Core Contributor",
        (2, 1): "Effective Contributor",
        (1, 3): "Enigma / Action Needed",
        (1, 2): "Dilemma / Inconsistent",
        (1, 1): "Underperformer / PIP Candidate"
    }

    def evaluate_workforce_performance(self, db: Session) -> Dict[str, Any]:
        employees = db.query(Employee).filter(Employee.status == "Active").all()

        matrix_items = []
        quadrant_counts = {v: 0 for v in self.QUADRANT_LABELS.values()}
        total_perf_sum = 0.0

        for emp in employees:
            review = db.query(PerformanceReview).filter(PerformanceReview.emp_id == emp.id).order_by(PerformanceReview.id.desc()).first()
            perf_val = review.manager_rating if review else emp.performance_rating
            pot_val = emp.potential_rating
            total_perf_sum += perf_val

            # Performance Tier (1: <3.0, 2: 3.0-4.0, 3: >4.0)
            perf_bucket = 3 if perf_val >= 4.2 else 2 if perf_val >= 3.0 else 1
            pot_bucket = max(1, min(3, pot_val))
            quadrant_name = self.QUADRANT_LABELS.get((perf_bucket, pot_bucket), "Core Contributor")
            quadrant_counts[quadrant_name] = quadrant_counts.get(quadrant_name, 0) + 1

            goal_pct = review.goal_completion_pct if review else 82.0
            sentiment_score = review.peer_sentiment_score if review else 4.0

            # Compute Promotion Readiness (0 - 100)
            # Factors: High performance, high potential, tenure > 18 months, strong peer sentiment
            tenure_factor = min(100.0, (emp.tenure_months / 24.0) * 100.0)
            promo_readiness = round(
                0.35 * (perf_val / 5.0 * 100.0) +
                0.30 * (pot_val / 3.0 * 100.0) +
                0.20 * (goal_pct) +
                0.15 * tenure_factor,
                1
            )

            # Recommendations
            if quadrant_name == "High Potential Star":
                rec_path = "Eligible for Promotion Evaluation; Fast-Track Leadership Development and Mentorship Assignment."
            elif quadrant_name in ["High Performer", "Core Contributor"]:
                rec_path = "Sustain Strong Domain Execution; Provide Advanced Cross-Functional Exposure."
            elif quadrant_name in ["High Potential Growth", "Enigma / Action Needed"]:
                rec_path = "Deepen Domain Coaching; Clarify Scope and Pair with Seasoned Peer Mentor."
            else:
                rec_path = "Structured 45-Day Remedial Coaching Sprint per Policy POL-PERF-2025."

            matrix_items.append({
                "emp_id": emp.id,
                "emp_code": emp.emp_code,
                "employee_name": f"{emp.first_name} {emp.last_name}",
                "department": emp.department_name,
                "role_title": emp.role_title,
                "performance_score": round(perf_val, 2),
                "potential_level": pot_val,
                "quadrant_name": quadrant_name,
                "goal_completion_pct": goal_pct,
                "sentiment_score": sentiment_score,
                "promotion_readiness_score": promo_readiness,
                "strengths": review.strengths_summary if review else "Consistent operational execution",
                "development_areas": review.growth_areas_summary if review else "Cross-team communication",
                "recommended_path": rec_path
            })

        avg_perf = round(total_perf_sum / max(1, len(employees)), 2)
        high_potential_count = quadrant_counts.get("High Potential Star", 0) + quadrant_counts.get("High Potential Growth", 0)
        coaching_needed_count = quadrant_counts.get("Underperformer / PIP Candidate", 0) + quadrant_counts.get("Enigma / Action Needed", 0)

        return {
            "average_performance": avg_perf,
            "total_evaluated_employees": len(employees),
            "high_potential_count": high_potential_count,
            "growth_coaching_needed_count": coaching_needed_count,
            "quadrant_distribution": quadrant_counts,
            "matrix_items": matrix_items,
            "governance_rule": "System provides decision support and readiness indicators; formal employment decisions must be verified and ratified by authorized HR leadership."
        }

performance_intel_service = PerformanceIntelligenceService()
