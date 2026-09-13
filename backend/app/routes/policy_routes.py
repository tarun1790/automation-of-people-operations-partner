from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.policy_reasoner import policy_intelligence_service

router = APIRouter(prefix="/policy", tags=["Policy Intelligence"])

class PolicyQueryRequest(BaseModel):
    query: str

@router.post("/query")
def query_hr_policy(request: PolicyQueryRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Source-grounded RAG query returning exact handbook title, section code, page number, and chunk excerpt."""
    return policy_intelligence_service.answer_query(db, request.query)
