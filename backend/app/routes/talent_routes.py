from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.hr_entities import JobPosting, RecruitmentCandidate, Interview
from backend.app.services.recruitment_engine import recruitment_engine
from backend.app.services.interview_agent import interview_intelligence_agent

router = APIRouter(prefix="/talent", tags=["Talent Intelligence"])

class QuestionGenRequest(BaseModel):
    role_title: str
    required_skills: List[str]

class AnswerEvalRequest(BaseModel):
    role_title: str
    question_text: str
    criteria: str
    candidate_answer: str

@router.get("/postings")
def list_job_postings(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    postings = db.query(JobPosting).all()
    results = []
    for p in postings:
        cands_count = db.query(RecruitmentCandidate).filter(RecruitmentCandidate.job_posting_id == p.id).count()
        results.append({
            "id": p.id,
            "req_code": p.req_code,
            "title": p.title,
            "department": p.department_name,
            "target_level": p.target_level,
            "min_experience_years": p.min_experience_years,
            "budget_salary_min": p.budget_salary_min,
            "budget_salary_max": p.budget_salary_max,
            "status": p.status,
            "required_skills": [s.strip() for s in p.required_skills_csv.split(",") if s.strip()],
            "preferred_skills": [s.strip() for s in p.preferred_skills_csv.split(",") if s.strip()],
            "job_description": p.job_description,
            "candidate_count": cands_count
        })
    return results

@router.get("/candidates/{posting_id}")
def rank_candidates_for_posting(
    posting_id: int,
    anonymize: bool = Query(False, description="Enable bias-mitigation anonymized evaluation"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    posting = db.query(JobPosting).filter(JobPosting.id == posting_id).first()
    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")

    candidates = db.query(RecruitmentCandidate).filter(RecruitmentCandidate.job_posting_id == posting_id).all()
    posting_data = {
        "id": posting.id,
        "title": posting.title,
        "required_skills_csv": posting.required_skills_csv,
        "preferred_skills_csv": posting.preferred_skills_csv,
        "min_experience_years": posting.min_experience_years,
        "job_description": posting.job_description
    }

    evaluations = []
    for c in candidates:
        cand_dict = {
            "id": c.id,
            "full_name": c.full_name,
            "anonymized_alias": c.anonymized_alias,
            "email": c.email,
            "years_of_experience": c.years_of_experience,
            "current_title": c.current_title,
            "resume_text": c.resume_text,
            "parsed_skills_csv": c.parsed_skills_csv,
            "stage": c.stage
        }
        ev = recruitment_engine.evaluate_candidate(cand_dict, posting_data, anonymize_bias=anonymize)
        evaluations.append(ev)

    # Sort descending by composite match score
    evaluations.sort(key=lambda x: x["composite_score"], reverse=True)
    return evaluations

@router.post("/interviews/generate-questions")
def generate_interview_questions(request: QuestionGenRequest) -> List[Dict[str, Any]]:
    """Generates structured role-specific questions and STAR criteria."""
    return interview_intelligence_agent.generate_role_questions(request.role_title, request.required_skills)

@router.post("/interviews/evaluate-answer")
def evaluate_candidate_answer(request: AnswerEvalRequest) -> Dict[str, Any]:
    """Analyzes candidate response depth, technical accuracy, and STAR methodology."""
    return interview_intelligence_agent.evaluate_response(
        role_title=request.role_title,
        question=request.question_text,
        criteria=request.criteria,
        candidate_answer=request.candidate_answer
    )
