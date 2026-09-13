from typing import Dict, Any, List
from datetime import datetime

class AdaptiveOnboardingAgent:
    """Generates personalized 30-60-90 day onboarding journeys based on role, department, and seniority."""

    ROLE_TEMPLATES = {
        "Engineering": {
            "Day 1-7": [
                ("Compliance", "Complete Security Compliance, SOC2 & Data Privacy Certification"),
                ("Tech Setup", "Provision Cloud sandbox, Git repository access, and local development container"),
                ("Team & Culture", "Initial 1-on-1 welcome session with Engineering Manager and assigned Peer Buddy")
            ],
            "Day 30": [
                ("Tech Setup", "Merge first production pull request and deploy through CI/CD pipeline"),
                ("Team & Culture", "Shadow primary on-call engineer and review system architecture blueprints"),
                ("Execution & Goal", "30-Day Alignment Check-in with HR People Partner")
            ],
            "Day 60": [
                ("Execution & Goal", "Own independent feature delivery from technical design to production release"),
                ("Tech Setup", "Participate in bi-weekly architectural review committee")
            ],
            "Day 90": [
                ("Execution & Goal", "Lead cross-functional technical retrospective and establish Q2 OKRs"),
                ("Team & Culture", "Complete 90-Day Comprehensive Onboarding Evaluation")
            ]
        },
        "Product & Design": {
            "Day 1-7": [
                ("Compliance", "Complete IP protection, user privacy, and compliance modules"),
                ("Tech Setup", "Gain access to Figma workspaces, Jira boards, and analytics dashboards"),
                ("Team & Culture", "Welcome meet-and-greet with Product Director and lead UX researchers")
            ],
            "Day 30": [
                ("Execution & Goal", "Conduct 5 customer feedback interviews and map user journey friction points"),
                ("Team & Culture", "30-Day Check-in with HR People Partner")
            ],
            "Day 60": [
                ("Execution & Goal", "Deliver finalized PRD and prototype spec for upcoming sprint release"),
                ("Team & Culture", "Facilitate cross-team alignment workshop between Design and Engineering")
            ],
            "Day 90": [
                ("Execution & Goal", "Present quarterly product roadmap vision to executive stakeholders"),
                ("Team & Culture", "Finalize 90-day onboarding review")
            ]
        },
        "People Operations": {
            "Day 1-7": [
                ("Compliance", "HRIS data confidentiality certification and employment law compliance"),
                ("Tech Setup", "Access HRIS, applicant tracking systems (ATS), and payroll portals"),
                ("Team & Culture", "Orientation with Chief People Officer and HR department leads")
            ],
            "Day 30": [
                ("Execution & Goal", "Shadow 10 candidate interviews and facilitate new hire orientation cohort"),
                ("Team & Culture", "30-Day People Partner review")
            ],
            "Day 60": [
                ("Execution & Goal", "Audit department retention metrics and propose compensation recalibrations"),
                ("Team & Culture", "Organize monthly employee pulse survey review")
            ],
            "Day 90": [
                ("Execution & Goal", "Lead departmental workforce planning cycle for upcoming fiscal half"),
                ("Team & Culture", "Complete 90-day comprehensive review")
            ]
        },
        "General": {
            "Day 1-7": [
                ("Compliance", "Complete mandatory corporate ethics, safety, and IT compliance courses"),
                ("Tech Setup", "Configure corporate email, Slack, password manager, and workspace credentials"),
                ("Team & Culture", "Meet team members and schedule initial 1-on-1 with direct manager")
            ],
            "Day 30": [
                ("Execution & Goal", "Complete initial onboarding project milestone"),
                ("Team & Culture", "30-Day Milestone Check-in with HR People Partner")
            ],
            "Day 60": [
                ("Execution & Goal", "Independently execute core departmental responsibilities"),
                ("Team & Culture", "Review mid-probation goals and progress")
            ],
            "Day 90": [
                ("Execution & Goal", "Deliver first full quarter deliverables and set upcoming OKRs"),
                ("Team & Culture", "Complete formal 90-day onboarding closure")
            ]
        }
    }

    def generate_journey_plan(
        self,
        emp_id: int,
        department: str,
        role_title: str,
        seniority: str = "Mid",
        tech_stack: List[str] = None
    ) -> Dict[str, Any]:
        template = self.ROLE_TEMPLATES.get(department, self.ROLE_TEMPLATES["General"])
        tasks = []

        for phase, task_list in template.items():
            for category, task_name in task_list:
                desc = f"Targeted milestone for {seniority} {role_title} within {department}."
                if tech_stack and category == "Tech Setup":
                    desc += f" Focus on: {', '.join(tech_stack)}."

                tasks.append({
                    "milestone_phase": phase,
                    "category": category,
                    "task_name": task_name,
                    "description": desc,
                    "is_completed": False,
                    "completed_date": None
                })

        return {
            "emp_id": emp_id,
            "department": department,
            "role_title": role_title,
            "seniority": seniority,
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "current_day": 1,
            "progress_pct": 0.0,
            "status": "Active",
            "assigned_buddy": f"Senior {role_title.split()[-1]} Mentor",
            "hr_mentor": "People Operations Partner",
            "tasks": tasks
        }

    def assess_pacing_status(self, current_day: int, total_tasks: int, completed_tasks: int) -> str:
        if total_tasks == 0:
            return "Active"

        completion_pct = (completed_tasks / total_tasks) * 100.0
        expected_pct = min(100.0, (current_day / 90.0) * 100.0)

        if completion_pct >= expected_pct + 15.0:
            return "Ahead"
        elif completion_pct < expected_pct - 20.0:
            return "AtRisk"
        elif completion_pct >= 100.0:
            return "Completed"
        else:
            return "Active"

onboarding_agent = AdaptiveOnboardingAgent()
