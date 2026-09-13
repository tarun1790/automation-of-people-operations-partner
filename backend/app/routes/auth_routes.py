from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.hr_entities import UserAccount
from backend.app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    user = db.query(UserAccount).filter(UserAccount.username == request.username).first()
    if not user or not auth_service.verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = auth_service.generate_token(user.username, user.role, user.full_name)
    permissions = auth_service.ROLE_PERMISSIONS.get(user.role, ["view_self"])

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role,
        "permissions": permissions
    }

@router.get("/me")
def get_current_user(authorization: str = Header(None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]
    payload = auth_service.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Session expired or invalid")

    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
        "full_name": payload.get("name"),
        "permissions": auth_service.ROLE_PERMISSIONS.get(payload.get("role"), [])
    }
