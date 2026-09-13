from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.hr_entities import Employee, AttendanceRecord, CompensationRecord

class DataQualityService:
    """Pre-flight HR data quality validation layer ensuring reliable ML inputs and governance."""

    def validate_workforce_data(self, db: Session) -> Dict[str, Any]:
        employees = db.query(Employee).all()
        total_records = len(employees)

        if total_records == 0:
            return {
                "data_quality_score": 100.0,
                "missing_values_pct": 0.0,
                "duplicates_pct": 0.0,
                "invalid_records_pct": 0.0,
                "validation_status": "Passed",
                "issues_detected": [],
                "last_validated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }

        issues = []
        missing_count = 0
        duplicate_count = 0
        invalid_count = 0

        seen_emails = set()
        seen_codes = set()

        for emp in employees:
            # 1. Duplicate Detection
            if emp.email in seen_emails:
                duplicate_count += 1
                issues.append({"type": "Duplicate Email", "entity": f"Employee {emp.emp_code}", "detail": f"Duplicate email {emp.email}"})
            else:
                seen_emails.add(emp.email)

            if emp.emp_code in seen_codes:
                duplicate_count += 1
                issues.append({"type": "Duplicate ID", "entity": f"Employee {emp.emp_code}", "detail": f"Duplicate code {emp.emp_code}"})
            else:
                seen_codes.add(emp.emp_code)

            # 2. Missing Value Checks
            if not emp.first_name or not emp.last_name or not emp.role_title:
                missing_count += 1
                issues.append({"type": "Missing Mandatory Field", "entity": f"Employee {emp.emp_code}", "detail": "Missing name or role title"})

            # 3. Range & Outlier Validation
            if emp.current_salary <= 0 or emp.market_salary_benchmark <= 0:
                invalid_count += 1
                issues.append({"type": "Invalid Compensation Value", "entity": f"Employee {emp.emp_code}", "detail": f"Salary must be > 0. Found: ${emp.current_salary}"})

            if not (1.0 <= emp.performance_rating <= 5.0):
                invalid_count += 1
                issues.append({"type": "Out of Range Rating", "entity": f"Employee {emp.emp_code}", "detail": f"Performance rating {emp.performance_rating} not in [1.0, 5.0]"})

            if not (0.0 <= emp.remote_work_ratio <= 1.0):
                invalid_count += 1
                issues.append({"type": "Invalid Remote Ratio", "entity": f"Employee {emp.emp_code}", "detail": f"Remote ratio {emp.remote_work_ratio} not in [0.0, 1.0]"})

        # Check Attendance Consistency
        attendances = db.query(AttendanceRecord).all()
        for att in attendances:
            if (att.days_present + att.days_absent) > (att.working_days + 2):
                invalid_count += 1
                issues.append({"type": "Attendance Inconsistency", "entity": f"Attendance #{att.id}", "detail": f"Days present ({att.days_present}) + absent ({att.days_absent}) exceeds working days ({att.working_days})"})

        total_checked = total_records * 5 + len(attendances)
        total_errors = missing_count + duplicate_count + invalid_count
        quality_score = max(0.0, min(100.0, round((1.0 - (total_errors / max(1, total_checked))) * 100.0, 1)))

        missing_pct = round((missing_count / max(1, total_records)) * 100.0, 1)
        duplicates_pct = round((duplicate_count / max(1, total_records)) * 100.0, 1)
        invalid_pct = round((invalid_count / max(1, total_records)) * 100.0, 1)

        return {
            "data_quality_score": quality_score,
            "missing_values_pct": missing_pct,
            "duplicates_pct": duplicates_pct,
            "invalid_records_pct": invalid_pct,
            "total_records_audited": total_records,
            "validation_status": "Healthy" if quality_score >= 90.0 else "Warning",
            "issues_detected": issues[:10],
            "last_validated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }

data_quality_service = DataQualityService()
