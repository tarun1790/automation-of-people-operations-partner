from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), unique=True, index=True)
    name = Column(String(64), nullable=False)
    head_name = Column(String(96))
    budget = Column(Float, default=1000000.0)

    employees = relationship("Employee", back_populates="department_rel")
    job_postings = relationship("JobPosting", back_populates="department_rel")

class RoleDefinition(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), unique=True, index=True)
    title = Column(String(96), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    seniority_band = Column(String(32), default="Mid")
    min_market_salary = Column(Float, default=70000.0)
    max_market_salary = Column(Float, default=110000.0)
    median_market_salary = Column(Float, default=90000.0)

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    emp_code = Column(String(32), unique=True, index=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    email = Column(String(128), unique=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), index=True)
    department_name = Column(String(64), index=True)
    role_title = Column(String(96), index=True)
    seniority_level = Column(String(32), default="Mid")
    tenure_months = Column(Integer, default=12)
    current_salary = Column(Float, default=75000.0)
    market_salary_benchmark = Column(Float, default=80000.0)
    performance_rating = Column(Float, default=3.5)  # 1.0 to 5.0
    potential_rating = Column(Integer, default=2)     # 1 (Low), 2 (Medium), 3 (High)
    months_since_last_promotion = Column(Integer, default=12)
    remote_work_ratio = Column(Float, default=0.4)   # 0.0 to 1.0
    commute_distance_km = Column(Float, default=15.0)
    manager_name = Column(String(96), default="Department Lead")
    status = Column(String(32), default="Active")    # Active, Resigned, OnLeave
    hire_date = Column(String(32), default="2023-01-15")
    pulse_satisfaction_score = Column(Float, default=7.5) # 1.0 to 10.0
    recognition_count = Column(Integer, default=4)
    training_hours_completed = Column(Float, default=18.0)

    # Relationships
    department_rel = relationship("Department", back_populates="employees")
    attendances = relationship("AttendanceRecord", back_populates="employee", cascade="all, delete-orphan")
    compensations = relationship("CompensationRecord", back_populates="employee", cascade="all, delete-orphan")
    reviews = relationship("PerformanceReview", back_populates="employee", cascade="all, delete-orphan")
    goals = relationship("GoalOKR", back_populates="employee", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback360", back_populates="employee", cascade="all, delete-orphan")
    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    trainings = relationship("TrainingRecord", back_populates="employee", cascade="all, delete-orphan")
    onboarding_journey = relationship("OnboardingJourney", back_populates="employee", uselist=False)

class CompensationRecord(Base):
    __tablename__ = "compensation_records"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Integer, ForeignKey("employees.id"), index=True)
    effective_date = Column(String(32), nullable=False)
    base_salary = Column(Float, nullable=False)
    market_median = Column(Float, nullable=False)
    compa_ratio = Column(Float, nullable=False) # base / market
    bonus_target_pct = Column(Float, default=10.0)
    equity_grant_usd = Column(Float, default=0.0)
    adjustment_reason = Column(String(64), default="Market Calibration")

    employee = relationship("Employee", back_populates="compensations")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Integer, ForeignKey("employees.id"), index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    working_days = Column(Integer, default=22)
    days_present = Column(Integer, default=21)
    days_absent = Column(Integer, default=1)
    unplanned_absences = Column(Integer, default=0)
    tardiness_count = Column(Integer, default=0)
    overtime_hours = Column(Float, default=0.0)
    weekend_hours = Column(Float, default=0.0)

    employee = relationship("Employee", back_populates="attendances")

class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Integer, ForeignKey("employees.id"), index=True)
    review_cycle = Column(String(32), default="2025-H2")
    goal_completion_pct = Column(Float, default=85.0)
    manager_rating = Column(Float, default=3.8) # 1.0 - 5.0
    peer_sentiment_score = Column(Float, default=4.0) # 1.0 - 5.0
    leadership_score = Column(Float, default=3.5)
    technical_score = Column(Float, default=4.0)
    collaboration_score = Column(Float, default=4.2)
    strengths_summary = Column(Text)
    growth_areas_summary = Column(Text)
    feedback_notes = Column(Text)
    nine_box_quadrant = Column(String(64), default="Core Contributor")
    promotion_readiness_score = Column(Float, default=70.0)

    employee = relationship("Employee", back_populates="reviews")

class GoalOKR(Base):
    __tablename__ = "goals_okrs"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Integer, ForeignKey("employees.id"), index=True)
    cycle = Column(String(32), default="2026-Q1")
    title = Column(String(128), nullable=False)
    metric_target = Column(String(64))
    progress_pct = Column(Float, default=0.0)
    status = Column(String(32), default="In Progress") # In Progress, Completed, Delayed

    employee = relationship("Employee", back_populates="goals")

class Feedback360(Base):
    __tablename__ = "feedback_360"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Integer, ForeignKey("employees.id"), index=True)
    reviewer_role = Column(String(32)) # Manager, Peer, Direct Report, Cross-functional
    sentiment_score = Column(Float, default=4.0) # 1.0 - 5.0
    sentiment_label = Column(String(32), default="Positive") # Positive, Neutral, Constructive
    comments = Column(Text)
    cycle = Column(String(32), default="2025-H2")

    employee = relationship("Employee", back_populates="feedbacks")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, index=True)
    category = Column(String(64), default="Technical")
    is_strategic_growth_skill = Column(Boolean, default=False)
    description = Column(String(256))

class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Integer, ForeignKey("employees.id"), index=True)
    skill_name = Column(String(64), index=True)
    category = Column(String(64), default="Technical")
    proficiency_level = Column(String(32), default="Intermediate") # Beginner, Intermediate, Advanced, Expert
    years_of_experience = Column(Float, default=2.0)
    is_critical_skill = Column(Boolean, default=False)

    employee = relationship("Employee", back_populates="skills")

class TrainingRecord(Base):
    __tablename__ = "training_records"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Integer, ForeignKey("employees.id"), index=True)
    course_name = Column(String(128), nullable=False)
    provider = Column(String(64), default="Internal Tech Academy")
    completion_date = Column(String(32))
    hours = Column(Float, default=8.0)
    score_pct = Column(Float, default=90.0)

    employee = relationship("Employee", back_populates="trainings")

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    req_code = Column(String(32), unique=True, index=True)
    title = Column(String(96), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    department_name = Column(String(64), index=True)
    target_level = Column(String(32), default="Mid")
    min_experience_years = Column(Float, default=3.0)
    budget_salary_min = Column(Float, default=85000.0)
    budget_salary_max = Column(Float, default=120000.0)
    status = Column(String(32), default="Open") # Open, InProgress, Filled, Paused
    required_skills_csv = Column(Text, default="")
    preferred_skills_csv = Column(Text, default="")
    job_description = Column(Text)
    created_date = Column(String(32), default="2026-01-10")

    department_rel = relationship("Department", back_populates="job_postings")
    candidates = relationship("RecruitmentCandidate", back_populates="job_posting", cascade="all, delete-orphan")

class RecruitmentCandidate(Base):
    __tablename__ = "recruitment_candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), index=True)
    full_name = Column(String(96), nullable=False)
    anonymized_alias = Column(String(64))
    email = Column(String(128))
    years_of_experience = Column(Float, default=4.0)
    current_title = Column(String(96))
    resume_text = Column(Text)
    parsed_skills_csv = Column(Text, default="")
    certifications_csv = Column(Text, default="")
    education = Column(String(128), default="B.S. Computer Science")
    skill_match_pct = Column(Float, default=0.0)
    experience_alignment_pct = Column(Float, default=0.0)
    education_score_pct = Column(Float, default=90.0)
    certifications_score_pct = Column(Float, default=85.0)
    composite_score = Column(Float, default=0.0)
    recommendation = Column(String(32), default="Pending") # Strong Hire, Consider, Do Not Hire
    stage = Column(String(32), default="Applied") # Applied, Screened, Interview, Offer, Rejected
    explanation_notes = Column(Text)

    job_posting = relationship("JobPosting", back_populates="candidates")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")

class OnboardingJourney(Base):
    __tablename__ = "onboarding_journeys"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Integer, ForeignKey("employees.id"), unique=True, index=True)
    department = Column(String(64))
    role_title = Column(String(96))
    cohort = Column(String(32), default="2026-Q1")
    start_date = Column(String(32))
    current_day = Column(Integer, default=1)
    progress_pct = Column(Float, default=0.0)
    status = Column(String(32), default="Active") # Active, Ahead, AtRisk, Completed
    assigned_buddy = Column(String(96), default="Senior Peer")
    hr_mentor = Column(String(96), default="HR People Partner")
    adaptive_notes = Column(Text)

    employee = relationship("Employee", back_populates="onboarding_journey")
    tasks = relationship("OnboardingTask", back_populates="journey", cascade="all, delete-orphan")

class OnboardingTask(Base):
    __tablename__ = "onboarding_tasks"

    id = Column(Integer, primary_key=True, index=True)
    journey_id = Column(Integer, ForeignKey("onboarding_journeys.id"), index=True)
    milestone_phase = Column(String(32), default="Day 1-7") # Day 1-7, Day 30, Day 60, Day 90
    category = Column(String(64), default="Technical Setup") # Compliance, Tech Setup, Team & Culture, Execution & Goal
    task_name = Column(String(128), nullable=False)
    description = Column(Text)
    is_completed = Column(Boolean, default=False)
    completed_date = Column(String(32), nullable=True)

    journey = relationship("OnboardingJourney", back_populates="tasks")

class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), unique=True, index=True)
    title = Column(String(128), nullable=False)
    category = Column(String(64), index=True)
    version = Column(String(16), default="4.0")
    effective_date = Column(String(32), default="2025-01-01")
    summary = Column(Text)

    chunks = relationship("PolicyChunk", back_populates="policy", cascade="all, delete-orphan")

class PolicyChunk(Base):
    __tablename__ = "policy_chunks"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), index=True)
    section_code = Column(String(32))
    section_title = Column(String(128))
    page_number = Column(Integer, default=1)
    chunk_text = Column(Text, nullable=False)

    policy = relationship("Policy", back_populates="chunks")

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("recruitment_candidates.id"), index=True)
    role_title = Column(String(96))
    interview_type = Column(String(64), default="Technical & Behavioral")
    interviewer_name = Column(String(96), default="Senior Engineering Lead")
    overall_score = Column(Float, default=0.0)
    recommendation = Column(String(32), default="Pending")
    strengths_summary = Column(Text)
    improvement_areas = Column(Text)
    conducted_at = Column(String(32), default="2026-02-20")

    candidate = relationship("RecruitmentCandidate", back_populates="interviews")
    evaluations = relationship("InterviewEvaluation", back_populates="interview", cascade="all, delete-orphan")

class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), index=True)
    question_text = Column(Text, nullable=False)
    candidate_answer = Column(Text)
    technical_accuracy_score = Column(Float, default=0.0)
    depth_score = Column(Float, default=0.0)
    clarity_score = Column(Float, default=0.0)
    star_structure_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    strengths_json = Column(Text)
    missing_aspects_json = Column(Text)
    actionable_feedback = Column(Text)

    interview = relationship("Interview", back_populates="evaluations")

class PredictionLog(Base):
    __tablename__ = "predictions_log"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(Integer, ForeignKey("employees.id"), index=True)
    model_version = Column(String(32), default="v2.4-CUDA")
    predicted_flight_risk = Column(Float, nullable=False)
    risk_tier = Column(String(32), nullable=False) # Low, Medium, High, Critical
    confidence_score = Column(Float, default=0.85)
    top_factors_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class RecommendationItem(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    target_type = Column(String(32), default="Employee") # Employee, Department, Org
    target_id = Column(Integer, nullable=True)
    target_name = Column(String(128))
    title = Column(String(128), nullable=False)
    category = Column(String(64)) # Compensation, Workload, Retention, Promotion, Upskilling, Coaching
    evidence = Column(Text)
    reasoning = Column(Text)
    confidence_score = Column(Float, default=0.85)
    recommended_action = Column(Text)
    expected_impact = Column(String(128))
    priority = Column(String(32), default="High") # Low, Medium, High, Critical
    status = Column(String(32), default="Pending Review") # Pending Review, Approved, Modified, Dismissed, Executed
    created_at = Column(DateTime, default=datetime.utcnow)

    action = relationship("HRAction", back_populates="recommendation", uselist=False)

class HRAction(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=True)
    action_type = Column(String(64), nullable=False)
    title = Column(String(128), nullable=False)
    target_entity = Column(String(128))
    reason = Column(Text)
    evidence = Column(Text)
    priority = Column(String(32), default="High")
    expected_impact = Column(String(128))
    status = Column(String(32), default="Pending Approval") # Pending Approval, Approved, Modified, Rejected, Executed
    approved_by = Column(String(96), nullable=True)
    human_notes = Column(Text, nullable=True)
    outcome_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    recommendation = relationship("RecommendationItem", back_populates="action")
    audit_logs = relationship("AuditLog", back_populates="action")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer, ForeignKey("actions.id"), nullable=True)
    event_type = Column(String(64), nullable=False) # Prediction, Recommendation, HumanDecision, Execution, PolicyInquiry
    model_version = Column(String(32), default="WorkSight-CUDA-v2.4")
    actor = Column(String(96), default="System") # System, HR Director, HR Manager, Admin
    summary = Column(Text, nullable=False)
    details_json = Column(Text) # Complete traceable JSON snapshot
    timestamp = Column(DateTime, default=datetime.utcnow)

    action = relationship("HRAction", back_populates="audit_logs")

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(64), nullable=False)
    version = Column(String(32), nullable=False)
    framework = Column(String(32), default="PyTorch 2.11 + CUDA")
    accuracy = Column(Float, default=0.912)
    precision = Column(Float, default=0.885)
    recall = Column(Float, default=0.873)
    f1_score = Column(Float, default=0.879)
    roc_auc = Column(Float, default=0.938)
    inference_latency_ms = Column(Float, default=2.4)
    training_date = Column(String(32), default="2026-02-15")
    is_active = Column(Boolean, default=True)

class UserAccount(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True)
    email = Column(String(128), unique=True, index=True)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(96))
    role = Column(String(32), default="HR Manager") # Admin, HR Director, HR Manager, Manager, Employee
    is_active = Column(Boolean, default=True)
