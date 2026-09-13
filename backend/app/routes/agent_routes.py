from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.services.autonomous_agent import autonomous_agent

agent_router = APIRouter(prefix="/agent", tags=["Autonomous Workforce Agent"])

class AgentMessageRequest(BaseModel):
    sender: Optional[str] = "Sarah Jenkins (HR Director)"
    message: str
    channel: Optional[str] = "Web Console"

class AgentModeRequest(BaseModel):
    mode: str  # "Autonomous" or "Supervised"

@agent_router.get("/status")
def get_status():
    """Retrieve the live operational status, telemetry, and mode of the autonomous agent."""
    return autonomous_agent.get_status()

@agent_router.post("/mode")
def set_agent_mode(req: AgentModeRequest):
    """Toggle between Autonomous (Auto-Pilot) and Supervised (Human-in-the-loop) mode."""
    res = autonomous_agent.set_mode(req.mode)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@agent_router.post("/patrol")
def trigger_patrol(db: Session = Depends(get_db)):
    """Trigger an immediate autonomous workforce patrol cycle across all departments."""
    return autonomous_agent.run_autonomous_patrol(db)

@agent_router.post("/message")
def send_message(req: AgentMessageRequest, db: Session = Depends(get_db)):
    """
    Ingest an incoming natural language message/instruction from a manager,
    employee, or external channel (Slack, Teams, Webhook).
    The agent autonomously evaluates, plans, simulates, and executes.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")
    return autonomous_agent.process_incoming_message(
        db=db,
        sender=req.sender,
        message_text=req.message,
        channel=req.channel
    )

@agent_router.get("/feed")
def get_activity_feed():
    """Retrieve chronological feed of autonomous decisions and actions executed by the agent."""
    return list(autonomous_agent.activity_feed)

class OnboardNewHireRequest(BaseModel):
    candidate_name: str
    role_title: str
    department: str
    personal_email: Optional[str] = None

@agent_router.post("/onboard-new-hire")
def onboard_new_hire(req: OnboardNewHireRequest, db: Session = Depends(get_db)):
    """
    Autonomously provisions company email, IT tools (Google Workspace, Slack, GitHub, Jira, VPN),
    hardware shipment, $1,200 workstation stipend, and 30-60-90 day milestone roadmap.
    """
    return autonomous_agent.provision_new_hire_automation(
        db=db,
        candidate_name=req.candidate_name,
        role_title=req.role_title,
        department=req.department,
        personal_email=req.personal_email
    )

@agent_router.get("/briefing")
def get_executive_briefing(db: Session = Depends(get_db)):
    """
    Retrieve the Proactive Executive Morning Briefing summarizing overnight operations,
    prevented turnover costs, Cherrington (1995) 7-function health, and daily recommendations.
    """
    return autonomous_agent.get_executive_briefing(db)

@agent_router.get("/sentinel/status")
def get_sentinel_status():
    """Retrieve telemetry of the continuous autonomous background sentinel daemon."""
    return autonomous_agent.get_status()["sentinel_daemon"]

@agent_router.post("/sentinel/tick")
def trigger_sentinel_tick():
    """Trigger an immediate heartbeat tick across Cherrington's 7 HRM functions."""
    return autonomous_agent.trigger_sentinel_tick()

@agent_router.get("/sentinel/research")
def get_personnel_research(db: Session = Depends(get_db)):
    """
    Retrieve empirical Personnel Research & Absenteeism analysis fulfilling
    Cherrington (1995) Function G and Lia Marthalia (2022) Benefit E.
    """
    return autonomous_agent.get_personnel_research(db)
