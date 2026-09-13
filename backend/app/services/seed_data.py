import json
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from backend.app.models.hr_entities import (
    Department,
    RoleDefinition,
    Employee,
    CompensationRecord,
    AttendanceRecord,
    PerformanceReview,
    GoalOKR,
    Feedback360,
    Skill,
    EmployeeSkill,
    TrainingRecord,
    JobPosting,
    RecruitmentCandidate,
    Interview,
    InterviewEvaluation,
    OnboardingJourney,
    OnboardingTask,
    Policy,
    PolicyChunk,
    RecommendationItem,
    HRAction,
    AuditLog,
    ModelVersion,
    UserAccount
)
from backend.app.services.auth_service import auth_service
from backend.app.services.audit_service import audit_action_service

def populate_database_if_empty(db: Session):
    existing_emp_count = db.query(Employee).count()
    if existing_emp_count > 0:
        return

    # 1. Seed Users (RBAC)
    users_data = [
        ("admin", "admin@worksight.ai", "admin123", "System Administrator", "Admin"),
        ("hr_director", "director@worksight.ai", "director123", "Sarah Jenkins", "HR Director"),
        ("hr_manager", "manager@worksight.ai", "manager123", "David Sterling", "HR Manager"),
        ("eng_lead", "marcus@worksight.ai", "lead123", "Marcus Vance", "Manager"),
        ("elena_r", "elena.rostova@techcorp.com", "user123", "Elena Rostova", "Employee")
    ]
    for uname, email, pwd, fname, role in users_data:
        db.add(UserAccount(
            username=uname,
            email=email,
            password_hash=auth_service.hash_password(pwd),
            full_name=fname,
            role=role,
            is_active=True
        ))
    db.commit()

    # 2. Seed Model Version
    db.add(ModelVersion(
        model_name="WorkSight-CUDA-AttritionNet",
        version="v2.4-CUDA",
        framework="PyTorch 2.11 + CUDA (RTX 3070 Ti)",
        accuracy=0.912,
        precision=0.885,
        recall=0.873,
        f1_score=0.879,
        roc_auc=0.938,
        inference_latency_ms=2.1,
        training_date="2026-02-15",
        is_active=True
    ))
    db.commit()

    # 3. Seed Departments
    dept_names = [
        ("Engineering", "Marcus Vance", 4500000.0),
        ("Product & Design", "Sarah Jenkins", 2100000.0),
        ("Data & AI", "Vikram Deshmukh", 2800000.0),
        ("Sales & Marketing", "Rachel Adams", 3200000.0),
        ("People Operations", "David Sterling", 1500000.0),
        ("Finance & Operations", "Patricia Hayes", 1800000.0)
    ]
    dept_map = {}
    for idx, (dname, dhead, dbudget) in enumerate(dept_names, 1):
        dept = Department(
            code=f"DEPT-{idx:02d}",
            name=dname,
            head_name=dhead,
            budget=dbudget
        )
        db.add(dept)
        db.flush()
        dept_map[dname] = dept
    db.commit()

    # 4. Seed Policy Documents and Chunks (Source-Grounded RAG)
    policy_specs = [
        {
            "code": "POL-LV-2025",
            "title": "Comprehensive Paid Leave and Absence Governance Policy",
            "category": "Leave & Absence",
            "version": "4.1",
            "summary": "Governs annual paid vacation, sick leave documentation, bereavement, and parental care leave.",
            "chunks": [
                ("SEC-1.1", "Section 1.1: Annual Paid Time Off (PTO)", 14,
                 "Full-time employees receive 24 days of paid vacation annually accrued at 2.0 days per calendar month. Up to 5 unused days may roll over into Q1 of the subsequent year. Leave requests exceeding 3 consecutive days require manager approval with at least 14 days advance notice."),
                ("SEC-1.2", "Section 1.2: Sick Leave and Medical Documentation", 16,
                 "Employees are entitled to 10 fully paid sick days annually. Unplanned medical absences exceeding 3 consecutive business days require an authenticated medical certificate from a licensed physician before payroll approval."),
                ("SEC-1.3", "Section 1.3: Parental & Primary Caregiver Leave", 18,
                 "Birthing and primary caregiver parents are granted 18 weeks of 100% paid parental leave. Secondary caregivers receive 8 weeks of 100% paid leave. Eligible after 90 days of continuous full-time employment. Flexible phased return-to-work is permitted with 80% schedule at 100% salary for the first 30 days post-leave.")
            ]
        },
        {
            "code": "POL-REM-2025",
            "title": "Flexible Hybrid Work and Remote Operations Framework",
            "category": "Remote & Hybrid",
            "version": "3.0",
            "summary": "Defines hybrid schedule guidelines, core working hours, ergonomic stipends, and overtime governance.",
            "chunks": [
                ("SEC-2.1", "Section 2.1: Hybrid Scheduling Guidelines", 8,
                 "Standard engineering and product teams operate under a 3:2 hybrid schedule (3 days on-site, 2 days remote). Core collaboration hours are 10:00 AM to 4:00 PM local time across all timezones. Full-remote exceptions require Department Head and People Ops Director approval."),
                ("SEC-2.2", "Section 2.2: Ergonomic Workspace Allowance", 11,
                 "Full-time permanent staff are eligible for a one-time $1,200 home workstation stipend upon passing probation, renewable every 36 months for display, ergonomic chair, or peripheral upgrades."),
                ("SEC-2.3", "Section 2.3: Overtime Governance in Remote Environments", 15,
                 "Non-exempt and exempt personnel must track and report hours exceeding standard 40-hour work weeks. Working over 15 hours of overtime in a single week triggers automated burnout risk review by HR People Partners.")
            ]
        },
        {
            "code": "POL-COMP-2025",
            "title": "Compensation Structure, Market Calibration, and Merit Guidelines",
            "category": "Compensation & Benefits",
            "version": "2.8",
            "summary": "Governs compa-ratio calibrations, retention bonuses, and promotional salary adjustments.",
            "chunks": [
                ("SEC-3.1", "Section 3.1: Compensation Ratio Benchmarking", 22,
                 "Salaries are pegged to the 75th percentile of regional tech sector benchmarks (Compa-Ratio 1.0). When an employee's compa-ratio drops below 0.88 due to market inflation, the HR Compensation Committee conducts mid-year salary parity reviews."),
                ("SEC-3.2", "Section 3.2: Spot Retention Bonus and Critical Skill Retention", 25,
                 "HR Directors may allocate discretionary retention bonuses of up to 20% base salary with a 12-month retention clawback clause for key personnel identified as single points of failure in mission-critical technology stacks."),
                ("SEC-3.3", "Section 3.3: Promotion Compensation Deltas", 28,
                 "Lateral promotion across engineering bands (e.g. Mid to Senior, Senior to Staff) guarantees a minimum base salary enhancement of 12% to 18%, effective the first day of the subsequent pay cycle.")
            ]
        },
        {
            "code": "POL-PERF-2025",
            "title": "Performance Management, 360 Reviews, and Performance Improvement Plans (PIP)",
            "category": "Performance & Growth",
            "version": "3.5",
            "summary": "Standardizes bi-annual OKR reviews, 9-box grid calibration, and 45-day remedial coaching plans.",
            "chunks": [
                ("SEC-4.1", "Section 4.1: Bi-Annual Performance Cycles & 9-Box Calibration", 33,
                 "Performance reviews evaluate objective goal completion (60%) and core competency 360 feedback (40%). Employees are classified on a 9-box grid across Performance (1 to 5 scale) and Potential (Low, Medium, High)."),
                ("SEC-4.2", "Section 4.2: Structured Coaching vs Performance Improvement Plans (PIP)", 36,
                 "Employees with a performance rating below 2.5 enter a formal 45-day Performance Improvement Plan. The PIP must document quantifiable weekly milestones, dedicated mentor pairing, and weekly check-in summaries. A score improvement to >= 3.0 successfully graduates the employee.")
            ]
        }
    ]

    for ps in policy_specs:
        policy = Policy(
            code=ps["code"],
            title=ps["title"],
            category=ps["category"],
            version=ps["version"],
            summary=ps["summary"]
        )
        db.add(policy)
        db.flush()

        for scode, stitle, pnum, ctext in ps["chunks"]:
            db.add(PolicyChunk(
                policy_id=policy.id,
                section_code=scode,
                section_title=stitle,
                page_number=pnum,
                chunk_text=ctext
            ))
    db.commit()

    # 5. Seed Core Employees & Longitudinal Records
    core_employees_data = [
        # Elena Rostova - Burnout & Retention Flight Risk
        {
            "code": "EMP-1001", "first": "Elena", "last": "Rostova", "email": "elena.rostova@techcorp.com",
            "dept": "Engineering", "role": "Senior Distributed Systems Engineer", "level": "Senior",
            "tenure": 28, "salary": 128000, "market": 158000, "perf": 4.6, "pot": 3, "promo_months": 24,
            "remote": 0.5, "commute": 22, "manager": "Marcus Vance", "sat": 4.2, "recognition": 2, "train_hrs": 12,
            "overtime": 32.5, "absent": 4, "tardiness": 3,
            "skills": [("Kubernetes", "Expert", True), ("Go", "Expert", False), ("Distributed Tracing", "Advanced", True), ("Kafka", "Advanced", False)],
            "review": {
                "cycle": "2025-H2", "goal": 96.0, "mgr": 4.7, "peer": 4.8, "lead": 4.5, "tech": 4.9, "collab": 4.4,
                "strengths": "Architected low-latency event ingestion pipeline processing 250k events/sec with zero loss.",
                "growth": "Severely over-burdened by continuous on-call shifts; feeling unrewarded relative to market rates.",
                "notes": "Elena expressed deep frustration regarding compensation falling 19% below peer benchmark.",
                "quadrant": "High Potential Star", "readiness": 88.0
            }
        },
        # Vikram Deshmukh - Critical Skill SPOF (Lead AI Architect)
        {
            "code": "EMP-1002", "first": "Vikram", "last": "Deshmukh", "email": "vikram.deshmukh@techcorp.com",
            "dept": "Data & AI", "role": "Lead Machine Learning Architect", "level": "Staff",
            "tenure": 36, "salary": 172000, "market": 185000, "perf": 4.8, "pot": 3, "promo_months": 14,
            "remote": 0.8, "commute": 12, "manager": "David Sterling", "sat": 8.5, "recognition": 8, "train_hrs": 35,
            "overtime": 14.0, "absent": 1, "tardiness": 0,
            "skills": [("PyTorch", "Expert", True), ("LLM Fine-Tuning", "Expert", True), ("CUDA Optimization", "Expert", True), ("Vector Databases", "Advanced", True)],
            "review": {
                "cycle": "2025-H2", "goal": 99.0, "mgr": 4.9, "peer": 4.7, "lead": 4.8, "tech": 5.0, "collab": 4.6,
                "strengths": "Sole deep specialist on high-performance CUDA kernels and RAG pipelines. Drives corporate AI strategy.",
                "growth": "High risk of single-point dependency; must cross-train teammates on model deployment pipelines.",
                "notes": "Critical technical pillar. High retention priority.",
                "quadrant": "High Potential Star", "readiness": 95.0
            }
        },
        # Chloe Dupond - Product Leader
        {
            "code": "EMP-1003", "first": "Chloe", "last": "Dupond", "email": "chloe.dupond@techcorp.com",
            "dept": "Product & Design", "role": "Senior Product Manager", "level": "Senior",
            "tenure": 22, "salary": 135000, "market": 138000, "perf": 4.1, "pot": 2, "promo_months": 10,
            "remote": 0.4, "commute": 8, "manager": "Sarah Jenkins", "sat": 7.9, "recognition": 5, "train_hrs": 20,
            "overtime": 6.5, "absent": 1, "tardiness": 1,
            "skills": [("Product Strategy", "Advanced", False), ("User Research", "Advanced", False), ("Agile Delivery", "Expert", False)],
            "review": {
                "cycle": "2025-H2", "goal": 88.0, "mgr": 4.1, "peer": 4.2, "lead": 4.0, "tech": 3.8, "collab": 4.4,
                "strengths": "Delivered candidate analytics suite on schedule with 40% adoption surge.",
                "growth": "Deepen technical understanding of backend data pipeline constraints.",
                "notes": "Solid dependable product leader.",
                "quadrant": "High Performer", "readiness": 75.0
            }
        },
        # Maya Lin - High Performer Ready for Promotion
        {
            "code": "EMP-1004", "first": "Maya", "last": "Lin", "email": "maya.lin@techcorp.com",
            "dept": "People Operations", "role": "People Operations Partner", "level": "Mid",
            "tenure": 20, "salary": 84000, "market": 92000, "perf": 4.4, "pot": 3, "promo_months": 18,
            "remote": 0.2, "commute": 14, "manager": "David Sterling", "sat": 8.8, "recognition": 6, "train_hrs": 28,
            "overtime": 4.0, "absent": 0, "tardiness": 0,
            "skills": [("Workforce Planning", "Advanced", False), ("Conflict Resolution", "Expert", False), ("HR Analytics", "Advanced", False)],
            "review": {
                "cycle": "2025-H2", "goal": 94.0, "mgr": 4.5, "peer": 4.6, "lead": 4.3, "tech": 4.0, "collab": 4.8,
                "strengths": "Reduced department time-to-hire by 18 days. High empathy and objective analytical problem solving.",
                "growth": "Ready to assume Senior People Partner scope managing engineering retention.",
                "notes": "Top candidate for lateral promotion.",
                "quadrant": "High Potential Star", "readiness": 90.0
            }
        },
        # Lucas Weber - Underperformer Needing Coaching
        {
            "code": "EMP-1005", "first": "Lucas", "last": "Weber", "email": "lucas.weber@techcorp.com",
            "dept": "Engineering", "role": "Backend Engineer", "level": "Junior",
            "tenure": 8, "salary": 68000, "market": 72000, "perf": 2.3, "pot": 1, "promo_months": 8,
            "remote": 0.6, "commute": 30, "manager": "Marcus Vance", "sat": 5.1, "recognition": 1, "train_hrs": 6,
            "overtime": 2.0, "absent": 5, "tardiness": 8,
            "skills": [("Python", "Intermediate", False), ("SQL", "Beginner", False), ("Git", "Intermediate", False)],
            "review": {
                "cycle": "2025-H2", "goal": 54.0, "mgr": 2.3, "peer": 2.8, "lead": 2.0, "tech": 2.5, "collab": 3.0,
                "strengths": "Receptive to code review feedback.",
                "growth": "Missed 3 critical sprint deliverables. Needs structured coaching on test-driven development.",
                "notes": "Recommend 45-day remedial coaching sprint per Policy POL-PERF-2025.",
                "quadrant": "Enigma / Action Needed", "readiness": 32.0
            }
        },
        # Amara Okonkwo - Active Onboarding New Hire
        {
            "code": "EMP-1006", "first": "Amara", "last": "Okonkwo", "email": "amara.okonkwo@techcorp.com",
            "dept": "Engineering", "role": "Cloud DevOps Engineer", "level": "Mid",
            "tenure": 1, "salary": 110000, "market": 112000, "perf": 3.5, "pot": 2, "promo_months": 1,
            "remote": 0.4, "commute": 10, "manager": "Marcus Vance", "sat": 8.0, "recognition": 2, "train_hrs": 15,
            "overtime": 0.0, "absent": 0, "tardiness": 0,
            "skills": [("Terraform", "Advanced", False), ("AWS", "Advanced", False), ("Docker", "Expert", False), ("CI/CD", "Advanced", False)],
            "review": {
                "cycle": "2026-H1", "goal": 80.0, "mgr": 3.5, "peer": 3.6, "lead": 3.5, "tech": 3.8, "collab": 3.7,
                "strengths": "Quick ramp-up. Successfully deployed first staging infrastructure on Day 14.",
                "growth": "Currently in Day 25 of 90-day onboarding journey.",
                "notes": "Pacing on track with assigned peer buddy.",
                "quadrant": "Core Contributor", "readiness": 55.0
            }
        }
    ]

    # Expand to 32 employees
    first_names = ["Noah", "Liam", "Emma", "Olivia", "Aria", "Ethan", "Zoe", "Alexander", "Mia", "Benjamin",
                   "Charlotte", "Amelia", "Henry", "Harper", "Sebastian", "Evelyn", "Jack", "Abigail",
                   "Daniel", "Emily", "Matthew", "Elizabeth", "Samuel", "Mila", "Ella", "Joseph"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
                  "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore"]

    depts = ["Engineering", "Product & Design", "Data & AI", "Sales & Marketing", "People Operations", "Finance & Operations"]
    titles = {
        "Engineering": ["Software Engineer", "Frontend Specialist", "QA Automation Engineer", "Site Reliability Engineer", "Platform Engineer"],
        "Product & Design": ["UI/UX Designer", "Product Designer", "User Researcher", "Product Operations Analyst"],
        "Data & AI": ["Data Engineer", "BI Analyst", "ML Engineer", "Data Analytics Specialist"],
        "Sales & Marketing": ["Enterprise Account Exec", "Customer Success Lead", "Sales Development Rep", "Growth Marketer"],
        "People Operations": ["HR Specialist", "Talent Acquisition Lead", "Compensation Analyst", "L&D Specialist"],
        "Finance & Operations": ["Financial Analyst", "Operations Manager", "Accounting Lead", "Procurement Specialist"]
    }

    random.seed(42)
    idx = 1007
    for i in range(26):
        dname = random.choice(depts)
        rtitle = random.choice(titles[dname])
        slevel = random.choice(["Junior", "Mid", "Senior", "Lead"])
        tenure = random.randint(4, 46)
        base = 60000 + (20000 if slevel == "Mid" else 45000 if slevel == "Senior" else 65000 if slevel == "Lead" else 0)
        salary = base + random.randint(-4000, 12000)
        market = salary * random.uniform(0.92, 1.18)
        perf = round(random.uniform(2.9, 4.6), 2)
        pot = random.choice([1, 2, 3])
        promo = random.randint(4, 28)
        remote = random.choice([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        commute = round(random.uniform(5.0, 42.0), 1)
        sat = round(random.uniform(4.8, 9.2), 1)
        overtime = round(random.uniform(0.0, 22.0), 1)
        absent = random.randint(0, 4)
        tardiness = random.randint(0, 4)

        fname = first_names[i % len(first_names)]
        lname = last_names[i % len(last_names)]

        core_employees_data.append({
            "code": f"EMP-{idx}",
            "first": fname,
            "last": lname,
            "email": f"{fname.lower()}.{lname.lower()}@techcorp.com",
            "dept": dname,
            "role": rtitle,
            "level": slevel,
            "tenure": tenure,
            "salary": salary,
            "market": market,
            "perf": perf,
            "pot": pot,
            "promo_months": promo,
            "remote": remote,
            "commute": commute,
            "manager": dept_map[dname].head_name,
            "sat": sat,
            "recognition": random.randint(2, 6),
            "train_hrs": random.randint(8, 25),
            "overtime": overtime,
            "absent": absent,
            "tardiness": tardiness,
            "skills": [
                (f"{dname} Core Competency", "Advanced", False),
                ("Communication & Synthesis", "Advanced", False),
                ("Problem Solving", "Expert", False)
            ],
            "review": {
                "cycle": "2025-H2",
                "goal": round(perf * 20.0, 1),
                "mgr": perf,
                "peer": round(perf + random.uniform(-0.2, 0.3), 1),
                "lead": round(perf + random.uniform(-0.3, 0.2), 1),
                "tech": round(perf + random.uniform(-0.2, 0.4), 1),
                "collab": round(perf + random.uniform(-0.2, 0.4), 1),
                "strengths": f"Reliable delivery within {dname}.",
                "growth": "Continue proactive knowledge sharing.",
                "notes": "Consistent delivery within standard range.",
                "quadrant": "High Performer" if perf > 4.0 else "Core Contributor" if perf >= 3.0 else "Growth Candidate",
                "readiness": round(perf * 18.0, 1)
            }
        })
        idx += 1

    # Insert into Database
    created_emps = []
    for emp_dict in core_employees_data:
        dept_obj = dept_map[emp_dict["dept"]]
        emp = Employee(
            emp_code=emp_dict["code"],
            first_name=emp_dict["first"],
            last_name=emp_dict["last"],
            email=emp_dict["email"],
            department_id=dept_obj.id,
            department_name=dept_obj.name,
            role_title=emp_dict["role"],
            seniority_level=emp_dict["level"],
            tenure_months=emp_dict["tenure"],
            current_salary=float(emp_dict["salary"]),
            market_salary_benchmark=float(emp_dict["market"]),
            performance_rating=float(emp_dict["perf"]),
            potential_rating=int(emp_dict["pot"]),
            months_since_last_promotion=int(emp_dict["promo_months"]),
            remote_work_ratio=float(emp_dict["remote"]),
            commute_distance_km=float(emp_dict["commute"]),
            manager_name=emp_dict["manager"],
            status="Active",
            hire_date=(datetime.now() - timedelta(days=emp_dict["tenure"] * 30)).strftime("%Y-%m-%d"),
            pulse_satisfaction_score=float(emp_dict["sat"]),
            recognition_count=int(emp_dict["recognition"]),
            training_hours_completed=float(emp_dict["train_hrs"])
        )
        db.add(emp)
        db.flush()
        created_emps.append((emp, emp_dict))

        # Compensation Record
        db.add(CompensationRecord(
            emp_id=emp.id,
            effective_date="2025-01-01",
            base_salary=float(emp_dict["salary"]),
            market_median=float(emp_dict["market"]),
            compa_ratio=round(float(emp_dict["salary"]) / max(1.0, float(emp_dict["market"])), 3),
            bonus_target_pct=10.0,
            equity_grant_usd=15000.0,
            adjustment_reason="Annual Compensation Calibration"
        ))

        # Attendance Record (6 months history)
        for m_offset in range(6):
            dt = datetime.now() - timedelta(days=30 * m_offset)
            m_ot = max(0.0, emp_dict["overtime"] + random.uniform(-3.0, 3.0))
            m_abs = max(0, emp_dict["absent"] + random.randint(-1, 1))
            db.add(AttendanceRecord(
                emp_id=emp.id,
                month=dt.month,
                year=dt.year,
                working_days=22,
                days_present=max(16, 22 - m_abs),
                days_absent=m_abs,
                unplanned_absences=min(m_abs, random.randint(0, m_abs)),
                tardiness_count=max(0, emp_dict["tardiness"] + random.randint(-1, 1)),
                overtime_hours=round(m_ot, 1),
                weekend_hours=round(max(0.0, m_ot * 0.2), 1)
            ))

        # Performance Review
        r = emp_dict["review"]
        db.add(PerformanceReview(
            emp_id=emp.id,
            review_cycle=r["cycle"],
            goal_completion_pct=r["goal"],
            manager_rating=r["mgr"],
            peer_sentiment_score=r["peer"],
            leadership_score=r["lead"],
            technical_score=r["tech"],
            collaboration_score=r["collab"],
            strengths_summary=r["strengths"],
            growth_areas_summary=r["growth"],
            feedback_notes=r["notes"],
            nine_box_quadrant=r["quadrant"],
            promotion_readiness_score=r["readiness"]
        ))

        # Skills
        for sk_name, sk_prof, sk_crit in emp_dict["skills"]:
            db.add(EmployeeSkill(
                emp_id=emp.id,
                skill_name=sk_name,
                category="Technical" if emp_dict["dept"] in ["Engineering", "Data & AI"] else "Operational",
                proficiency_level=sk_prof,
                years_of_experience=round(emp_dict["tenure"] / 12.0 + 1.5, 1),
                is_critical_skill=sk_crit
            ))

    db.commit()

    # 6. Seed Onboarding Journey for Amara (EMP-1006)
    amara = next(e for e, d in created_emps if d["code"] == "EMP-1006")
    amara_journey = OnboardingJourney(
        emp_id=amara.id,
        department=amara.department_name,
        role_title=amara.role_title,
        cohort="2026-Q1",
        start_date=(datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d"),
        current_day=25,
        progress_pct=60.0,
        status="Active",
        assigned_buddy="Elena Rostova (Staff Peer)",
        hr_mentor="Maya Lin (People Ops Partner)",
        adaptive_notes="Pacing on track; milestone completion rate 60% vs 55% cohort average."
    )
    db.add(amara_journey)
    db.flush()

    tasks_amara = [
        ("Day 1-7", "Compliance", "Complete Security Compliance & Data Privacy Certification", True, "Day 3"),
        ("Day 1-7", "Tech Setup", "Provision AWS Sandbox, Terraform credentials, and GitHub Enterprise access", True, "Day 2"),
        ("Day 1-7", "Team & Culture", "Attend 1-on-1 welcome session with Engineering Director Marcus Vance", True, "Day 4"),
        ("Day 30", "Tech Setup", "Deploy sample microservice infrastructure to staging Kubernetes cluster", True, "Day 18"),
        ("Day 30", "Team & Culture", "Complete 30-Day Check-in review with HR Mentor Maya Lin", False, None),
        ("Day 60", "Execution & Goal", "Refactor production CI/CD Terraform pipelines for latency reduction", False, None),
        ("Day 90", "Execution & Goal", "Lead architecture review for quarterly multi-region failover", False, None)
    ]
    for ph, cat, tname, is_done, cdate in tasks_amara:
        db.add(OnboardingTask(
            journey_id=amara_journey.id,
            milestone_phase=ph,
            category=cat,
            task_name=tname,
            description=f"Standard onboarding milestone for {amara.role_title}",
            is_completed=is_done,
            completed_date=cdate
        ))
    db.commit()

    # 7. Seed Job Postings & Candidates (Talent Intelligence)
    eng_dept = dept_map["Engineering"]
    ai_dept = dept_map["Data & AI"]

    post1 = JobPosting(
        req_code="REQ-ENG-2026-01",
        title="Senior Cloud Infrastructure Architect",
        department_id=eng_dept.id,
        department_name=eng_dept.name,
        target_level="Senior",
        min_experience_years=5.0,
        budget_salary_min=140000.0,
        budget_salary_max=175000.0,
        status="Open",
        required_skills_csv="Kubernetes, Terraform, AWS, Go, Distributed Systems, CI/CD",
        preferred_skills_csv="Prometheus, Kafka, Python, Rust, Zero Trust Security",
        job_description="Architect and scale multi-region Kubernetes deployments, enhance zero-downtime microservice orchestration, and automate infrastructure as code across hybrid cloud environments.",
        created_date="2026-01-15"
    )

    post2 = JobPosting(
        req_code="REQ-AI-2026-02",
        title="Generative AI & LLM Systems Engineer",
        department_id=ai_dept.id,
        department_name=ai_dept.name,
        target_level="Senior",
        min_experience_years=4.0,
        budget_salary_min=150000.0,
        budget_salary_max=190000.0,
        status="Open",
        required_skills_csv="PyTorch, CUDA Optimization, LLM Fine-Tuning, Vector Databases, Python",
        preferred_skills_csv="Hugging Face, vLLM, DeepSpeed, Triton, LangChain",
        job_description="Lead the design and execution of production LLM fine-tuning, high-throughput GPU inference pipelines, and contextual retrieval engines.",
        created_date="2026-02-01"
    )
    db.add(post1)
    db.add(post2)
    db.commit()

    # Candidates for REQ-ENG-2026-01
    cand1 = RecruitmentCandidate(
        job_posting_id=post1.id,
        full_name="Marcus Aurelius Sterling",
        anonymized_alias="Candidate Alpha (Masked)",
        email="m.sterling.tech@example.com",
        years_of_experience=7.5,
        current_title="Lead Site Reliability Architect at CloudScale Labs",
        resume_text="""Senior Cloud Architect with 7.5 years specializing in enterprise Kubernetes, Terraform infrastructure orchestration, and AWS multi-account governance.
Architected high-resiliency cloud environments supporting 10M+ daily active sessions. Built automated CI/CD deployment pipelines using Go and GitHub Actions.
Deep expertise in distributed systems tracing, Prometheus monitoring, and container networking. Led team of 6 DevOps engineers.
Skills: Kubernetes, Terraform, AWS, Go, Distributed Systems, CI/CD, Prometheus, Docker, Linux, Python.""",
        parsed_skills_csv="Kubernetes, Terraform, AWS, Go, Distributed Systems, CI/CD, Prometheus, Docker",
        certifications_csv="AWS Certified Solutions Architect Professional, CKA Certified Kubernetes Administrator",
        education="B.S. Computer Engineering",
        skill_match_pct=94.5,
        experience_alignment_pct=95.0,
        education_score_pct=95.0,
        certifications_score_pct=98.0,
        composite_score=94.8,
        recommendation="Strong Hire",
        stage="Technical Interview",
        explanation_notes="Candidate demonstrates comprehensive mastery of core Kubernetes distributed patterns and exceeds minimum experience requirement."
    )

    cand2 = RecruitmentCandidate(
        job_posting_id=post1.id,
        full_name="Priya Sharma",
        anonymized_alias="Candidate Beta (Masked)",
        email="priya.sharma.dev@example.com",
        years_of_experience=5.0,
        current_title="Cloud Engineer at DataMesh Networks",
        resume_text="""Cloud and DevOps Engineer with 5 years experience in AWS, Terraform automation, and Docker containerization.
Implemented automated deployment scripts and cost-optimization monitoring. Strong Python scripting and intermediate Kubernetes cluster management.
Skills: AWS, Terraform, Docker, Python, Kubernetes, CI/CD, Linux, Bash.""",
        parsed_skills_csv="AWS, Terraform, Docker, Python, Kubernetes, CI/CD",
        certifications_csv="AWS Solutions Architect Associate",
        education="B.S. Information Technology",
        skill_match_pct=78.0,
        experience_alignment_pct=85.0,
        education_score_pct=90.0,
        certifications_score_pct=85.0,
        composite_score=81.2,
        recommendation="Consider",
        stage="Screening",
        explanation_notes="Solid cloud foundation with minor gaps in large-scale distributed tracing and high-throughput Go microservices."
    )

    cand3 = RecruitmentCandidate(
        job_posting_id=post1.id,
        full_name="Arthur Pendelton",
        anonymized_alias="Candidate Gamma (Masked)",
        email="arthur.pendelton@example.com",
        years_of_experience=2.0,
        current_title="Junior Systems Administrator",
        resume_text="""Junior Systems Administrator with 2 years of IT operations experience. Basic knowledge of AWS console and Linux bash scripting.
Seeking transition into Cloud DevOps.
Skills: Linux, Bash, AWS, Git.""",
        parsed_skills_csv="Linux, Bash, AWS, Git",
        certifications_csv="CompTIA Security+",
        education="A.S. Network Systems",
        skill_match_pct=32.0,
        experience_alignment_pct=40.0,
        education_score_pct=80.0,
        certifications_score_pct=60.0,
        composite_score=35.5,
        recommendation="Do Not Hire",
        stage="Rejected",
        explanation_notes="Candidate does not meet the 5-year minimum seniority requirement or essential distributed Kubernetes competencies."
    )

    db.add(cand1)
    db.add(cand2)
    db.add(cand3)
    db.commit()

    # 8. Seed Interview & STAR Evaluation for Candidate Alpha
    interview1 = Interview(
        candidate_id=cand1.id,
        role_title="Senior Cloud Infrastructure Architect",
        interview_type="Technical Systems Architecture & Problem Solving",
        interviewer_name="Elena Rostova (Staff Lead)",
        overall_score=91.5,
        recommendation="Strong Hire",
        strengths_summary="Exceptional grasp of multi-cluster Kubernetes topology, graceful degradation, and distributed state management.",
        improvement_areas="None noted during the technical depth assessment.",
        conducted_at="2026-02-20"
    )
    db.add(interview1)
    db.flush()

    db.add(InterviewEvaluation(
        interview_id=interview1.id,
        question_text="How would you design a zero-downtime deployment strategy for a stateful distributed microservice running on Kubernetes across multiple availability zones?",
        candidate_answer="I would deploy the application using Kubernetes StatefulSets with distinct PersistentVolumeClaims bound to EBS gp3 volumes in each availability zone. To enforce zero downtime during upgrades, I configure PodDisruptionBudgets ensuring minimum available replicas remain >= 2, coupled with custom Readiness Probes that poll internal health checks before traffic ingress. Upgrades are rolled out partition by partition while monitoring error rates via Prometheus.",
        technical_accuracy_score=95.0,
        depth_score=94.0,
        clarity_score=92.0,
        star_structure_score=92.0,
        overall_score=93.5,
        strengths_json=json.dumps(["Thorough architectural precision", "Addressed storage persistence, availability quorum, and automated rollback triggers"]),
        missing_aspects_json=json.dumps(["Minor: could elaborate on cross-AZ egress latency costs"]),
        actionable_feedback="Demonstrates staff-level mastery of Kubernetes distributed storage and graceful pod eviction semantics."
    ))
    db.commit()

    # 9. Seed Recommendations, Actions & Audit Trail
    elena = next(e for e, d in created_emps if d["code"] == "EMP-1001")
    rec1 = RecommendationItem(
        target_type="Employee",
        target_id=elena.id,
        target_name=f"{elena.first_name} {elena.last_name}",
        title="Execute Retention Compensation Adjustment for Elena Rostova",
        category="Compensation & Retention",
        evidence="Compa-ratio is 0.81 (-19% vs market benchmark of $158k), sustained overtime at 32.5 hrs/mo, pulse score dropped to 4.2/10, no promotion for 24 months.",
        reasoning="Multi-source correlation shows high flight risk driven by compensation deficit and burnout exhaustion in a mission-critical distributed systems role.",
        confidence_score=0.88,
        recommended_action="Approve immediate 15% base salary recalibration ($128k -> $147.2k) and enforce on-call shift rotation cap of 8h/mo.",
        expected_impact="Reduces estimated flight risk from 78% to <20%, preventing catastrophic domain knowledge drain.",
        priority="Critical",
        status="Pending Review"
    )
    db.add(rec1)
    db.flush()

    action1 = HRAction(
        recommendation_id=rec1.id,
        action_type="Retention Intervention",
        title=f"Execute Retention Package for Elena Rostova ({elena.emp_code})",
        target_entity=f"Elena Rostova (Engineering)",
        reason="Model estimates elevated attrition risk (78%) based on compound workload and compensation disparity.",
        evidence="Overtime: 32.5 hrs/mo (Safety norm: 15h); Compa-ratio: 0.81 ($30,000 deficit); Pulse: 4.2/10; Review rating: 4.6/5.0 (Top Performer).",
        priority="Critical",
        expected_impact="Prevents departure of core Distributed Systems specialist; stabilizes engineering infrastructure operations.",
        status="Pending Approval",
        approved_by=None
    )
    db.add(action1)
    db.commit()

    # Log Creation in Audit Trail
    audit_action_service.log_event(
        db=db,
        event_type="RecommendationGenerated",
        summary="WorkSight AI generated Critical Retention recommendation for Elena Rostova (EMP-1001).",
        actor="WorkSight-Reasoning-Core",
        action_id=action1.id,
        details={
            "employee_id": elena.id,
            "flight_risk_estimated": 0.78,
            "evidence_signals": ["Overtime +32.5h", "Compa-Ratio 0.81", "Pulse 4.2", "Tenure 28m"],
            "model_version": "v2.4-CUDA"
        }
    )

    # Action 2: Launch Cross-Training Cohort
    rec2 = RecommendationItem(
        target_type="Department",
        target_id=ai_dept.id,
        target_name="Data & AI Department",
        title="Launch Cross-Training Cohort for CUDA Optimization & LLM Systems",
        category="Upskilling",
        evidence="Workforce Skill Graph detects Vikram Deshmukh as a single point of failure on CUDA optimization and LLM Fine-Tuning.",
        reasoning="Critical skill vulnerability leaves organizational AI strategy exposed to single-person availability risk.",
        confidence_score=0.94,
        recommended_action="Form 4-week internal cohort pairing Vikram with 3 senior backend engineers to distribute CUDA and vLLM competencies.",
        expected_impact="Eliminates critical SPOF vulnerability and expands internal generative AI capacity.",
        priority="High",
        status="Pending Review"
    )
    db.add(rec2)
    db.flush()

    action2 = HRAction(
        recommendation_id=rec2.id,
        action_type="Upskilling Program",
        title="Launch Cross-Training Cohort for CUDA Optimization & LLM Systems",
        target_entity="Data & AI Department",
        reason="Single Point of Failure vulnerability identified in Workforce Skill Graph.",
        evidence="Only 1 employee possessing Expert proficiency in CUDA Optimization; team skill coverage at 64%.",
        priority="High",
        expected_impact="Reduces single-point organizational risk; upskills 3 internal engineers.",
        status="Pending Approval"
    )
    db.add(action2)
    db.commit()

    audit_action_service.log_event(
        db=db,
        event_type="RecommendationGenerated",
        summary="WorkSight AI generated High-Priority Upskilling recommendation for Data & AI department.",
        actor="WorkSight-Reasoning-Core",
        action_id=action2.id,
        details={"department": "Data & AI", "vulnerability": "SPOF on CUDA Optimization"}
    )
