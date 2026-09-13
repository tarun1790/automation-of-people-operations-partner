from typing import Dict, Any, List, Tuple
import networkx as nx
from sqlalchemy.orm import Session
from backend.app.models.hr_entities import Employee, EmployeeSkill, Department, JobPosting

class WorkforceSkillGraphService:
    """Graph-based skill mapping and single-point-of-failure vulnerability detection using NetworkX."""

    def build_network_graph(self, db: Session) -> nx.DiGraph:
        G = nx.DiGraph()

        employees = db.query(Employee).filter(Employee.status == "Active").all()
        for emp in employees:
            emp_node = f"EMP_{emp.id}"
            G.add_node(
                emp_node,
                label=f"{emp.first_name} {emp.last_name}",
                type="employee",
                department=emp.department_name,
                role=emp.role_title
            )

            # Link to Department
            dept_node = f"DEPT_{emp.department_name.replace(' ', '_')}"
            G.add_node(dept_node, label=emp.department_name, type="department")
            G.add_edge(emp_node, dept_node, relationship="belongs_to", weight=1.0)

        # Add Skills and Edges
        emp_skills = db.query(EmployeeSkill).all()
        for es in emp_skills:
            emp_node = f"EMP_{es.emp_id}"
            skill_node = f"SKILL_{es.skill_name.replace(' ', '_')}"
            G.add_node(
                skill_node,
                label=es.skill_name,
                type="skill",
                category=es.category,
                is_critical=es.is_critical_skill
            )
            prof_weight = 4.0 if es.proficiency_level == "Expert" else 3.0 if es.proficiency_level == "Advanced" else 2.0 if es.proficiency_level == "Intermediate" else 1.0
            G.add_edge(emp_node, skill_node, relationship="possesses", proficiency=es.proficiency_level, weight=prof_weight)

        return G

    def get_graph_data(self, db: Session) -> Dict[str, Any]:
        G = self.build_network_graph(db)

        nodes = []
        for n, data in G.nodes(data=True):
            in_degree = G.in_degree(n) if data.get("type") == "skill" else None
            nodes.append({
                "id": n,
                "label": data.get("label", n),
                "type": data.get("type", "unknown"),
                "category": data.get("category"),
                "proficiency": data.get("proficiency"),
                "department": data.get("department"),
                "role": data.get("role"),
                "emp_count": in_degree
            })

        links = []
        for u, v, data in G.edges(data=True):
            links.append({
                "source": u,
                "target": v,
                "relationship": data.get("relationship", "connected"),
                "weight": data.get("weight", 1.0),
                "proficiency": data.get("proficiency")
            })

        # Detect Single Points of Failure (SPOFs)
        # Skills possessed by only 1 employee with Advanced or Expert proficiency
        spofs = []
        skill_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "skill"]
        for sk in skill_nodes:
            possessors = [u for u, v, d in G.in_edges(sk, data=True) if d.get("proficiency") in ["Advanced", "Expert"]]
            if len(possessors) == 1:
                holder_id = possessors[0]
                holder_data = G.nodes[holder_id]
                sk_data = G.nodes[sk]
                spofs.append({
                    "skill_name": sk_data.get("label"),
                    "category": sk_data.get("category", "Technical"),
                    "holder_name": holder_data.get("label"),
                    "holder_department": holder_data.get("department"),
                    "holder_role": holder_data.get("role"),
                    "holder_count": 1,
                    "vulnerability_level": "CRITICAL SINGLE POINT OF FAILURE",
                    "mitigation_plan": f"Launch immediate cross-training cohort pairing {holder_data.get('label')} with 2 internal engineers."
                })

        # Department Skill Coverage
        dept_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "department"]
        dept_coverage = {}
        for dn in dept_nodes:
            dept_name = G.nodes[dn].get("label")
            dept_emps = [u for u, v in G.in_edges(dn)]
            dept_skills = set()
            for de in dept_emps:
                for _, sk in G.out_edges(de):
                    if G.nodes[sk].get("type") == "skill":
                        dept_skills.add(G.nodes[sk].get("label"))
            coverage_score = min(100.0, len(dept_skills) * 9.5 + 20.0)
            dept_coverage[dept_name] = round(coverage_score, 1)

        return {
            "nodes": nodes,
            "links": links,
            "critical_single_points_of_failure": spofs,
            "department_skill_coverage": dept_coverage,
            "total_skills_tracked": len(skill_nodes)
        }

    def compute_internal_mobility_path(self, db: Session, emp_id: int, target_role: str) -> Dict[str, Any]:
        emp = db.query(Employee).filter(Employee.id == emp_id).first()
        if not emp:
            return {"error": "Employee not found"}

        current_skills = db.query(EmployeeSkill).filter(EmployeeSkill.emp_id == emp_id).all()
        current_skill_set = {s.skill_name.lower(): s.proficiency_level for s in current_skills}

        # Role requirements lookup
        role_reqs = {
            "Lead Machine Learning Architect": ["pytorch", "llm fine-tuning", "cuda optimization", "vector databases", "distributed tracing"],
            "Senior Distributed Systems Engineer": ["kubernetes", "go", "distributed tracing", "kafka", "terraform"],
            "Cloud DevOps Specialist": ["terraform", "aws", "docker", "ci/cd", "kubernetes"],
            "Lead People Partner": ["workforce planning", "conflict resolution", "hr analytics", "talent acquisition", "executive coaching"]
        }

        target_reqs = role_reqs.get(target_role, ["python", "sql", "communication", "leadership"])

        matched = []
        missing = []
        for req in target_reqs:
            if req in current_skill_set:
                matched.append({"skill": req.title(), "current_proficiency": current_skill_set[req]})
            else:
                missing.append({"skill": req.title(), "recommended_course": f"Advanced {req.title()} Certification"})

        readiness_pct = round((len(matched) / max(1, len(target_reqs))) * 100.0, 1)

        return {
            "employee_id": emp.id,
            "employee_name": f"{emp.first_name} {emp.last_name}",
            "current_role": emp.role_title,
            "target_role": target_role,
            "readiness_pct": readiness_pct,
            "matched_competencies": matched,
            "missing_competencies": missing,
            "recommended_learning_path": [m["recommended_course"] for m in missing],
            "estimated_readiness_timeline": f"{max(3, len(missing) * 2)} months of targeted upskilling"
        }

skill_graph_service = WorkforceSkillGraphService()
