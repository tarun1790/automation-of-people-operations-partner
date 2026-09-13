from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# Employee & Workforce Schemas
class EmployeeBase(BaseModel):
    emp_code: str
    first_name: str
    last_name: str
    email: str
    department: str
    role_title: str
    seniority_level: str = "Mid"
    tenure_months: int = 12
    salary: float = 75000.0
    market_salary_benchmark: float = 80000.0
    performance_rating: float = 3.5
    potential_rating: int = 2
    months_since_last_promotion: int = 12
    remote_work_ratio: float = 0.4
    commute_distance_km: float = 15.0
    manager_name: str = "Operations Lead"
    status: str = "Active"
    hire_date: str = "2023-01-15"
    pulse_satisfaction_score: float = 7.5

class EmployeeOut(EmployeeBase):
    id: int
    class Config:
        from_attributes = True

class AttendanceOut(BaseModel):
    id: int
    emp_id: int
    month: int
    year: int
    working_days: int
    days_present: int
    days_absent: int
    unplanned_absences: int
    tardiness_count: int
    overtime_hours: float
    weekend_hours: float
    class Config:
        from_attributes = True

# Recruitment Schemas
class CandidateRankRequest(BaseModel):
    requisition_id: int
    anonymize_bias: bool = False

class CandidateOut(BaseModel):
    id: int
    requisition_id: int
    full_name: str
    anonymized_alias: Optional[str] = None
    email: Optional[str] = None
    years_of_experience: float
    current_title: Optional[str] = None
    parsed_skills: List[str] = []
    skill_match_pct: float
    experience_alignment_pct: float
    composite_score: float
    recommendation: str
    stage: str
    key_strengths: List[str] = []
    skill_gaps: List[str] = []
    class Config:
        from_attributes = True

class RequisitionOut(BaseModel):
    id: int
    req_code: str
    title: str
    department: str
    target_level: str
    min_experience_years: float
    budget_salary_min: float
    budget_salary_max: float
    status: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    job_description: Optional[str] = None
    candidate_count: int = 0
    class Config:
        from_attributes = True

# Onboarding Schemas
class GenerateOnboardingRequest(BaseModel):
    employee_id: int
    target_department: Optional[str] = None
    role_title: Optional[str] = None
    seniority: Optional[str] = "Mid"
    tech_stack: Optional[List[str]] = None

class TaskUpdate(BaseModel):
    task_id: int
    is_completed: bool

class OnboardingTaskOut(BaseModel):
    id: int
    journey_id: int
    milestone_phase: str
    category: str
    task_name: str
    description: Optional[str] = None
    is_completed: bool
    completed_date: Optional[str] = None
    class Config:
        from_attributes = True

class OnboardingJourneyOut(BaseModel):
    id: int
    emp_id: int
    employee_name: str
    department: str
    role_title: str
    start_date: str
    current_day: int
    progress_pct: float
    status: str
    assigned_buddy: str
    hr_mentor: str
    tasks: List[OnboardingTaskOut] = []
    class Config:
        from_attributes = True

# Policy Reasoning Schemas
class PolicyQueryRequest(BaseModel):
    query: str
    department: Optional[str] = None
    context_role: Optional[str] = None

class PolicyCitation(BaseModel):
    policy_code: str
    title: str
    section_title: str
    citation_text: str
    relevance_score: float

class PolicyQueryResponse(BaseModel):
    query: str
    answer: str
    confidence_score: float
    citations: List[PolicyCitation]
    recommended_hr_action: Optional[str] = None

# Attrition Prediction Schemas
class AttritionFactor(BaseModel):
    feature_name: str
    contribution_score: float # positive increases risk, negative decreases
    description: str

class AttritionPredictionOut(BaseModel):
    emp_id: int
    employee_name: str
    department: str
    role_title: str
    flight_risk_score: float # 0.0 to 1.0
    risk_level: str # Low, Medium, High, Critical
    tenure_months: int
    salary_ratio_vs_market: float
    overtime_monthly_avg: float
    top_risk_factors: List[AttritionFactor]
    protective_factors: List[AttritionFactor]
    retention_playbook: str

# Performance Intelligence & 9-Box Schemas
class NineBoxItem(BaseModel):
    emp_id: int
    employee_name: str
    department: str
    role_title: str
    performance_score: float
    potential_level: int
    quadrant_name: str
    goal_completion_pct: float
    sentiment_score: float
    recommended_path: str

class PerformanceAnalyticsOut(BaseModel):
    average_performance: float
    high_potential_count: int
    growth_coaching_needed_count: int
    quadrant_distribution: Dict[str, int]
    matrix_items: List[NineBoxItem]

# Workforce Skill Graph Schemas
class SkillNode(BaseModel):
    id: str
    label: str
    type: str # 'skill', 'employee', 'department'
    category: Optional[str] = None
    proficiency: Optional[str] = None
    emp_count: Optional[int] = None

class SkillLink(BaseModel):
    source: str
    target: str
    relationship: str # 'possesses', 'requires', 'belongs_to'
    weight: float = 1.0

class SkillGraphData(BaseModel):
    nodes: List[SkillNode]
    links: List[SkillLink]
    critical_single_points_of_failure: List[Dict[str, Any]]
    department_skill_coverage: Dict[str, float]

class UpskillingPathRequest(BaseModel):
    employee_id: int
    target_role: str

# Interview Agent Schemas
class GenerateQuestionsRequest(BaseModel):
    role_title: str
    seniority: str
    required_skills: List[str]
    focus_areas: Optional[List[str]] = None

class InterviewQuestionOut(BaseModel):
    id: int
    question_text: str
    category: str
    competency: str
    evaluation_criteria: str
    sample_excellent_response: str

class EvaluateResponseRequest(BaseModel):
    role_title: str
    question_text: str
    expected_criteria: str
    candidate_answer: str

class InterviewEvaluationOut(BaseModel):
    relevance_score: float # 0-100
    technical_accuracy_score: float # 0-100
    star_structure_score: float # 0-100
    depth_score: float # 0-100
    overall_score: float # 0-100
    strengths: List[str]
    missing_aspects: List[str]
    hire_signal: str # Strong Hire, Hire, Leaning Hire, Do Not Hire
    actionable_feedback: str

# Cross-Source Reasoning & Dashboard Schemas
class CrossReasoningQueryRequest(BaseModel):
    query: str
    target_department: Optional[str] = None

class CrossReasoningDiagnosis(BaseModel):
    query: str
    executive_summary: str
    correlations_found: List[str]
    affected_headcount: int
    risk_severity: str
    prescribed_actions: List[Dict[str, Any]]
    supporting_evidence: Dict[str, Any]

class HRActionApprovalRequest(BaseModel):
    action_id: int
    decision: str # Approved, Dismissed, Executed
    notes: Optional[str] = None

class DashboardSummaryOut(BaseModel):
    total_headcount: int
    active_attrition_risk_pct: float
    avg_performance_rating: float
    open_requisitions_count: int
    absenteeism_rate_pct: float
    skill_health_index: float
    pending_critical_actions: int
    hardware_accelerator: str
    framework_grounding: Dict[str, Any]
