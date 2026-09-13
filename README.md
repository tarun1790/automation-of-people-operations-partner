# Atlas

### Your 24/7 Autonomous People Operations Partner
**Tagline**: *Your 24/7 Autonomous People Operations Partner.*

**Live Interactive Demo**: [https://tarun1790.github.io/automation-of-people-operations-partner/](https://tarun1790.github.io/automation-of-people-operations-partner/)

---

## 1. Executive Overview

**Atlas** is an enterprise-grade autonomous people operations platform that unifies fragmented HR data into an explainable, self-operating intelligence and decision layer. Operating continuously in the background, Atlas transforms workforce management from a series of manual tasks into a closed-loop autonomous system:

$$\text{Data} \longrightarrow \text{Correlation} \longrightarrow \text{Detection} \longrightarrow \text{Explanation} \longrightarrow \text{Prediction} \longrightarrow \text{Recommendation} \longrightarrow \text{Simulation} \longrightarrow \text{Auto-Execution} \longrightarrow \text{Outcome Monitoring}$$

### Core People Operations Architecture
The platform architecture is directly mapped to 7 core human capital operations functions:
1. **Staffing & Employment**: Talent acquisition, candidate resume vectorization, and structured competency interviews.
2. **Performance Evaluation**: Multi-source appraisal, 9-box talent matrix calibration, OKR tracking, and promotion readiness.
3. **Compensation & Benefits**: Compa-ratio market alignment, retention bonuses, and equity delta forecasting.
4. **Training & Development**: Workforce skill ontology, critical dependency detection, and adaptive 30-60-90 day onboarding roadmaps.
5. **Employee Relations**: Pulse sentiment analysis, psychological safety monitoring, and dispute prevention.
6. **Safety & Health**: Operational overtime governance, burnout thresholds, and workload rebalancing.
7. **Personnel Research & Analytics**: Deep learning attrition modeling, counterfactual scenario simulation, and demographic parity audits.

---

## 2. Core Architecture & Architectural Separation

Atlas enforces strict separation between three core layers:

| Layer | Question Answered | Implementation | Example Output |
| :--- | :--- | :--- | :--- |
| **Machine Learning** | *What is likely to happen?* | PyTorch CUDA Deep Neural Net (`WorkforceAttritionNet`) | Attrition probability: 78% (Risk: HIGH) |
| **Analytics & Rules** | *What changed and what signals are present?* | Statistical aggregation & anomaly radar | Overtime $+37\%$, compensation $14\%$ below market median |
| **AI Reasoning Layer** | *How do these signals relate, and what should HR investigate?* | Cross-Source Workforce Reasoning Engine | Compound retention vulnerability driven by uncompensated workload fatigue |

```
                 UNIFIED WORKFORCE DATA
                           │
                           ▼
                 DATA QUALITY PIPELINE
                           │
                           ▼
          ┌──────────────────────────────────┐
          │  CROSS-SOURCE REASONING ENGINE   │
          │                                  │
          │  Correlation • Root Cause        │
          │  Anomaly Detection • Prediction  │
          │  Recommendation • Simulation     │
          └────────────────┬─────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    TALENT    │    │  WORKFORCE   │    │   EMPLOYEE   │
│ INTELLIGENCE │    │ INTELLIGENCE │    │ INTELLIGENCE │
├──────────────┤    ├──────────────┤    ├──────────────┤
│ Recruitment  │    │ Attrition    │    │ Performance  │
│ Interviews   │    │ Attendance   │    │ Skills Graph │
│ Bias Monitor │    │ Compensation │    │ Onboarding   │
└──────────────┘    └──────────────┘    └──────────────┘
                           │
                           ▼
                 POLICY INTELLIGENCE
                 Source-Grounded RAG
                           │
                           ▼
                 DECISION GOVERNANCE
         Human-in-the-Loop Action Center
              + Immutable Audit Trail
```

---

## 3. Platform Modules & Features

### Module 1: Cross-Source Workforce Reasoning Engine & AI Command Center
- **Cross-Silo Synthesis**: Unifies attendance logs (overtime, absenteeism), compensation ratios, review trajectories, tenure, and skill dependencies.
- **Natural Language Command Center**: Responds to strategic prompts (e.g. *"Why is Engineering showing increased attrition?"*, *"What skills will we lack if we expand our AI team?"*) using structured database tool execution.
- **Standardized AI Insight Cards**: Every insight delivers `Finding`, `Evidence`, `Confidence %`, `Recommended Action`, and direct `[Review]` `[Simulate]` `[Dismiss]` triggers.

### Module 2: Workforce Risk Radar & PyTorch CUDA Prediction Engine
- **Hardware Acceleration**: Deep neural network (`WorkforceAttritionNet`) running on **NVIDIA GeForce RTX 3070 Ti Laptop GPU** via PyTorch CUDA.
- **Defensible Phrasing**: Replaces unsupportable claims with calibrated language:
  > *"The model estimates elevated attrition risk based on observed historical patterns."*
- **SHAP Explainability**: Decomposes individual flight risks into positive contributing drivers (overtime, compa-ratio gap) and protective buffers (peer sentiment, training hours).

### Module 3: What-If Counterfactual Scenario Simulator
- Quantitative perturbation model modeling the impact of:
  - Overtime reduction ($-10\%$ to $-40\%$)
  - Base compensation adjustment ($+0\%$ to $+15\%$)
  - Promotion cycle acceleration ($0$ to $12$ months)
  - Additional team staffing ($+1$ to $+8$)
- Calculates projected attrition delta, departures prevented, turnover replacement cost savings, and net annual financial benefit.

### Module 4: HR Action Center & Complete Audit Trail
- **Human-in-the-Loop Governance**: The system recommends; authorized HR leadership reviews, modifies, approves, or rejects.
- **Decision Audit Trail**: Immutable log tracking `Input Data`, `Model Version`, `Prediction`, `Evidence`, `Recommendation`, `Human Decision`, `Final Action`, and `Outcome`.

### Module 5: Talent Intelligence & Intelligent Interview Agent
- **Recruitment Engine**: Parses candidate resumes against multi-parameter job specifications, computing skill match %, experience alignment %, and composite scores.
- **Bias-Aware Mode**: Anonymizes candidate names, emails, and demographic proxies to ensure merit-based shortlisting.
- **STAR Interview Evaluator**: Role-specific dynamic question generation and real-time response scoring across Technical Accuracy, Depth, STAR Structure, and Communication.

### Module 6: Performance Intelligence & 9-Box Matrix
- Automates bi-annual appraisal calibrations and performance distribution.
- Maps workforce into a 9-box grid across **Performance** and **Potential**.
- Generates promotion readiness scores and remedial coaching paths per company guidelines.

### Module 7: Workforce Skill Graph & Mobility Pathfinder
- Graph-based skill topology using **NetworkX**.
- **Critical Dependency Alerts**: Detects Single Points of Failure (SPOFs) where critical skills are held by only 1 employee.
- **Internal Mobility Pathfinder**: Maps employee current competencies against target roles to recommend shortest upskilling curricula and timelines.

### Module 8: Adaptive Onboarding Agent
- Automatically provisions dynamic 30-60-90 day milestone roadmaps tailored to role, seniority, and tech stack.
- Evaluates completion velocity to dynamically categorize pacing as *Ahead*, *On Track*, or *At Risk*.

### Module 9: HR Policy Intelligence (Source-Grounded RAG)
- Vector retrieval over company policy handbooks (Paid Leave, Remote Work, Compa-Ratio, PIP Coaching).
- Delivers exact document titles, section codes, page numbers, and verbatim chunk excerpts.
- **Zero-Hallucination Fallback**: Returns *"No supporting policy was found in the available HR knowledge base"* when inquiries fall outside established guidelines.

### Module 10: Data Quality & Fairness Monitoring Layer
- **Data Quality Pipeline**: Pre-flight validation scanning for missing values, duplicates, out-of-range ratings, and attendance contradictions.
- **Fairness Monitor**: Tracks adverse impact ratios against the EEOC 4/5ths rule (0.80 benchmark) and verifies zero protected-attribute proxy leakage.

---

## 4. Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, Pydantic v2.
- **Machine Learning & Deep Learning**: PyTorch 2.11+ (CUDA enabled for NVIDIA RTX 3070 Ti), Scikit-Learn, XGBoost, SHAP.
- **Graph & Semantic Analytics**: NetworkX, TF-IDF Vectorization, Cosine Similarity.
- **Frontend**: Responsive Single-Page Application (SPA) with Tailwind CSS, Chart.js, Canvas graph rendering, and Lucide icons.
- **Database**: Normalized SQLite store (PostgreSQL-compatible architecture).
- **Testing**: Pytest with automated unit and integration suites.

---

## 5. Quick Start & Execution

### Prerequisites
- Python 3.10 or higher
- NVIDIA CUDA Toolkit & GPU (optional; falls back gracefully to CPU if CUDA is unavailable)

### Installation
```powershell
# Clone or navigate to the project directory
cd "c:\projects\HR AGENT"

# Install project dependencies
pip install -r requirements.txt
```

### Running Automated Tests
```powershell
python -m pytest backend/tests/ -v
```

### Launching the Platform
```powershell
python run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```
- **Executive Dashboard**: `http://127.0.0.1:8000/`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`
- **Health & Hardware Acceleration Endpoint**: `http://127.0.0.1:8000/health`
