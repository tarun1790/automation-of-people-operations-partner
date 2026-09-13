// Atlas Client-Side Mock Provider for GitHub Pages static hosting
(function() {
    const isStaticHost = window.location.hostname.includes('github.io') || 
                         window.location.protocol === 'file:' || 
                         window.location.port === '' || 
                         window.location.port === '5500';

    if (!isStaticHost) return;

    const originalFetch = window.fetch;

    const mockState = {
        agentMode: "Autonomous",
        actions: [
            { action_id: 1, recommendation_id: 1, action_type: "Workload Rebalancing", title: "Cap On-Call Overtime at 8h/mo for Elena Rostova", target_entity: "Elena Rostova", priority: "Critical", expected_impact: "Drops flight risk from 78.4% to 18.2%", status: "Approved" },
            { action_id: 2, recommendation_id: 2, action_type: "Compensation Calibration", title: "Benchmark Parity Adjustment for Distributed Systems Core", target_entity: "Engineering Team", priority: "High", expected_impact: "Closes 16% market gap, prevents 3.6 departures", status: "Pending Approval" }
        ],
        audit: [
            { id: 101, timestamp: "2026-09-13 17:45:12", event_type: "ModelPrediction", actor: "Atlas-CUDA-v2.4", summary: "Estimated flight risk for Elena Rostova at 78.4% based on 32.4h overtime and 0.84 compa-ratio.", model_version: "Atlas-CUDA-v2.4" },
            { id: 102, timestamp: "2026-09-13 17:50:00", event_type: "AutonomousPatrol", actor: "Atlas Autonomous Agent", summary: "Completed organization health patrol across 6 departments. Flagged 3 staff for retention review.", model_version: "Atlas-CUDA-v2.4" }
        ],
        tasks: [
            { id: 1, is_completed: true, task_name: "Complete Security Compliance, SOC2 & Data Privacy Certification", milestone_phase: "Day 1-7", category: "Compliance" },
            { id: 2, is_completed: true, task_name: "Provision Cloud sandbox, Git repository access, and container", milestone_phase: "Day 1-7", category: "Tech Setup" },
            { id: 3, is_completed: false, task_name: "Initial 1-on-1 welcome session with Engineering Manager and assigned Peer Buddy", milestone_phase: "Day 1-7", category: "Team & Culture" },
            { id: 4, is_completed: false, task_name: "Merge first production pull request and deploy through CI/CD", milestone_phase: "Day 30", category: "Tech Setup" }
        ]
    };

    window.fetch = async function(url, options = {}) {
        const u = typeof url === 'string' ? url : url.url;
        
        // Only intercept /api/v1 requests
        if (!u.includes('/api/v1')) {
            return originalFetch.apply(this, arguments);
        }

        const method = (options.method || 'GET').toUpperCase();
        let body = {};
        if (options.body) {
            try { body = JSON.parse(options.body); } catch(e) {}
        }

        const makeResponse = (data, status = 200) => {
            return new Response(JSON.stringify(data), {
                status: status,
                headers: { 'Content-Type': 'application/json' }
            });
        };

        // 1. Dashboard Summary
        if (u.includes('/dashboard/summary')) {
            return makeResponse({
                total_employees: 32,
                high_risk_employees: 3,
                workforce_health_score: 84,
                average_performance: 3.8,
                open_positions: 2,
                skill_coverage_pct: 89.2,
                pending_actions_count: mockState.actions.filter(a => a.status === 'Pending Approval').length,
                critical_spofs_count: 4
            });
        }

        // 2. Risk Radar
        if (u.includes('/dashboard/risk-radar')) {
            return makeResponse({
                department_risk_matrix: [
                    { department: "Engineering", risk_level: "CRITICAL", risk_score: 82, headcount: 12, detected_signals: ["Sustained overtime averaging 32.4h/month", "Compa-ratio 16% below market benchmark", "4 single-point-of-failure skill dependencies"], metrics: { avg_overtime_hrs: 32.4 } },
                    { department: "Product & Design", risk_level: "HIGH", risk_score: 68, headcount: 6, detected_signals: ["Overtime averaging 18.5h/month", "Promotion gap exceeding 18 months"], metrics: { avg_overtime_hrs: 18.5 } },
                    { department: "Sales & Marketing", risk_level: "MODERATE", risk_score: 48, headcount: 5, detected_signals: ["Quota attainment variation across Q3"], metrics: { avg_overtime_hrs: 8.0 } },
                    { department: "Data & AI", risk_level: "LOW", risk_score: 24, headcount: 4, detected_signals: ["Normal operational cadence and competitive compensation"], metrics: { avg_overtime_hrs: 5.2 } },
                    { department: "People Operations", risk_level: "LOW", risk_score: 18, headcount: 3, detected_signals: ["Healthy pulse scores and balanced workloads"], metrics: { avg_overtime_hrs: 3.0 } },
                    { department: "Finance & Legal", risk_level: "LOW", risk_score: 15, headcount: 2, detected_signals: ["All retention metrics within safe thresholds"], metrics: { avg_overtime_hrs: 2.5 } }
                ]
            });
        }

        // 3. AI Insights
        if (u.includes('/dashboard/insights')) {
            return makeResponse([
                {
                    badge: "Retention Alert",
                    confidence: 88,
                    target: "Elena Rostova (Engineering)",
                    finding: "Cross-source analysis demonstrates severe operational burnout compounded by a 16% compensation deficit.",
                    evidence: ["Overtime at 32.4h/mo (safety limit 15h)", "Compa-ratio is 0.84 ($18,000 below market median)", "Promotion gap of 19 months without career advancement"],
                    recommended_action: "Execute targeted retention calibration: cap on-call overtime and schedule compensation parity review."
                },
                {
                    badge: "Succession Opportunity",
                    confidence: 92,
                    target: "Marcus Brody (Product & Design)",
                    finding: "Candidate demonstrates sustained top-tier performance (4.6/5.0) and high leadership aptitude.",
                    evidence: ["Goal / OKR completion at 94.5%", "Positive 360 peer feedback rating (4.8/5.0)", "18 months in current role ready for Lead advancement"],
                    recommended_action: "Nominate for lateral promotion to Lead Product Partner with 15% salary calibration."
                },
                {
                    badge: "Skill Risk",
                    confidence: 94,
                    target: "Kubernetes & Distributed Tracing",
                    finding: "Single Point of Failure: only 1 staff member holds expert mastery in core infrastructure.",
                    evidence: ["Critical dependency on Elena Rostova", "Lack of secondary on-call coverage for production incidents"],
                    recommended_action: "Launch internal cross-training cohort and open secondary Distributed Systems requisition."
                }
            ]);
        }

        // 4. What-If Simulation
        if (u.includes('/simulation/simulate')) {
            const ot = body.overtime_delta_pct || -25;
            const sal = body.salary_delta_pct || 5;
            const promo = body.promotion_acceleration_months || 6;
            const baseRisk = 78.4;
            const reduction = Math.abs(ot) * 1.1 + sal * 1.5 + promo * 1.2;
            const projRisk = Math.max(12.0, Math.round((baseRisk - reduction) * 10) / 10);
            const delta = Math.round((baseRisk - projRisk) * 10) / 10;
            const prevented = Math.round((delta / 100 * 12) * 10) / 10;
            const savings = Math.round(prevented * 45000);
            const netRoi = Math.round(savings - (12 * 75000 * (sal / 100)));

            return makeResponse({
                department: body.department || "Engineering",
                current_state: { attrition_risk_pct: baseRisk },
                projected_state: { attrition_risk_pct: projRisk },
                impact_analysis: {
                    estimated_improvement_pp: delta,
                    departures_prevented_annually: prevented,
                    turnover_replacement_savings_usd: savings,
                    net_annual_financial_benefit_usd: netRoi
                },
                model_disclaimer: "Model-based counterfactual projection derived from neural network feature sensitivity."
            });
        }

        // 5. Actions
        if (u.includes('/governance/actions')) {
            if (u.includes('/review')) {
                const parts = u.split('/');
                const id = parseInt(parts[parts.indexOf('actions') + 1]);
                const act = mockState.actions.find(a => a.action_id === id);
                if (act) act.status = body.decision;
                return makeResponse({ success: true, action_id: id, status: body.decision });
            }
            return makeResponse(mockState.actions);
        }

        // 6. Audit Trail
        if (u.includes('/governance/audit-trail')) {
            return makeResponse(mockState.audit);
        }

        // 7. Attrition Predictions
        if (u.includes('/workforce/attrition-predictions')) {
            return makeResponse([
                { employee_code: "EMP-1001", employee_name: "Elena Rostova", department: "Engineering", role_title: "Senior Distributed Systems Engineer", attrition_probability: 0.784, risk_level: "CRITICAL", top_contributing_factors: [{ impact_pct: "+38%", factor: "Excessive monthly overtime (32.4 hrs)" }, { impact_pct: "+24%", factor: "Compa-ratio deficit (0.84 vs peer market)" }], defensible_statement: "The model estimates elevated attrition risk based on observed historical patterns." },
                { employee_code: "EMP-1002", employee_name: "Liam O'Connor", department: "Product & Design", role_title: "Staff Product Designer", attrition_probability: 0.682, risk_level: "HIGH", top_contributing_factors: [{ impact_pct: "+31%", factor: "Stagnant promotion timeline (18 mos)" }, { impact_pct: "+22%", factor: "Overtime logged (18.5 hrs)" }], defensible_statement: "The model estimates elevated attrition risk based on observed historical patterns." },
                { employee_code: "EMP-1003", employee_name: "Sophia Chen", department: "Data & AI", role_title: "Lead Machine Learning Architect", attrition_probability: 0.185, risk_level: "LOW", top_contributing_factors: [{ impact_pct: "-25%", factor: "High peer recognition and competitive salary" }], defensible_statement: "The model estimates low attrition probability with strong retention signals." },
                { employee_code: "EMP-1004", employee_name: "Devon Bailey", department: "Sales & Marketing", role_title: "Enterprise Account Executive", attrition_probability: 0.485, risk_level: "MODERATE", top_contributing_factors: [{ impact_pct: "+18%", factor: "Commission variance and travel fatigue" }], defensible_statement: "The model estimates moderate risk within normal quota cycles." }
            ]);
        }

        // 8. Talent Postings & Candidates
        if (u.includes('/talent/postings')) {
            return makeResponse([
                { id: 1, req_code: "REQ-2025-01", title: "Senior Distributed Systems Engineer", candidate_count: 3 }
            ]);
        }
        if (u.includes('/talent/candidates/')) {
            return makeResponse([
                { id: 101, full_name: "Elena Rostova", years_of_experience: 6.5, current_title: "Distributed Infrastructure Architect", composite_score: 92.4, skill_match_pct: 94.0, experience_alignment_pct: 90.0, recommendation: "Strong Hire", stage: "Interview", key_strengths: ["Go", "Kubernetes", "Distributed Tracing", "Kafka"], skill_gaps: [] },
                { id: 102, full_name: "Lucas Meyer", years_of_experience: 4.0, current_title: "Backend Cloud Developer", composite_score: 74.2, skill_match_pct: 70.0, experience_alignment_pct: 80.0, recommendation: "Consider", stage: "Screening", key_strengths: ["Docker", "Go"], skill_gaps: ["Kafka", "Distributed Tracing"] },
                { id: 103, full_name: "Maya Patel", years_of_experience: 2.0, current_title: "Junior Systems Engineer", composite_score: 52.0, skill_match_pct: 45.0, experience_alignment_pct: 60.0, recommendation: "Do Not Hire", stage: "Screening", key_strengths: ["Python"], skill_gaps: ["Kubernetes", "Distributed Tracing", "Go"] }
            ]);
        }

        // 9. Performance Matrix
        if (u.includes('/workforce/performance-matrix')) {
            return makeResponse({
                average_performance: 3.8,
                high_potential_count: 4,
                growth_coaching_needed_count: 2,
                quadrant_distribution: {
                    "High Potential Star": 4,
                    "High Performer": 8,
                    "High Potential Growth": 5,
                    "Core Contributor": 10,
                    "Solid Professional": 3,
                    "Effective Contributor": 1,
                    "Underperformer / PIP Candidate": 1
                },
                matrix_items: [
                    { employee_name: "Sophia Chen", department: "Data & AI", role_title: "Lead ML Architect", performance_score: 4.8, quadrant_name: "High Potential Star", promotion_readiness_score: 96, recommended_path: "Fast-track promotion to Principal Staff" },
                    { employee_name: "Elena Rostova", department: "Engineering", role_title: "Senior Distributed Engineer", performance_score: 4.5, quadrant_name: "High Potential Star", promotion_readiness_score: 92, recommended_path: "Staff Engineer with workload balancing" },
                    { employee_name: "Marcus Brody", department: "Product & Design", role_title: "Lead Product Partner", performance_score: 4.6, quadrant_name: "High Potential Star", promotion_readiness_score: 94, recommended_path: "Director of Product track" }
                ]
            });
        }

        // 10. Skills Graph
        if (u.includes('/workforce/skills-graph')) {
            return makeResponse({
                nodes: [
                    { id: "e1", label: "Elena Rostova", type: "employee" },
                    { id: "e2", label: "Sophia Chen", type: "employee" },
                    { id: "e3", label: "Marcus Brody", type: "employee" },
                    { id: "s1", label: "Kubernetes", type: "skill" },
                    { id: "s2", label: "PyTorch CUDA", type: "skill" },
                    { id: "s3", label: "Distributed Tracing", type: "skill" },
                    { id: "s4", label: "Go", type: "skill" },
                    { id: "s5", label: "Product Vision", type: "skill" }
                ],
                links: [
                    { source: "e1", target: "s1" },
                    { source: "e1", target: "s3" },
                    { source: "e1", target: "s4" },
                    { source: "e2", target: "s2" },
                    { source: "e3", target: "s5" }
                ],
                critical_single_points_of_failure: [
                    { skill_name: "Kubernetes", holder_name: "Elena Rostova", holder_department: "Engineering", mitigation_plan: "Schedule peer mentoring with secondary SRE staff." },
                    { skill_name: "PyTorch CUDA", holder_name: "Sophia Chen", holder_department: "Data & AI", mitigation_plan: "Conduct 4-week internal deep learning cohort." }
                ],
                department_skill_coverage: {
                    "Engineering": 92,
                    "Data & AI": 88,
                    "Product & Design": 85,
                    "People Operations": 94
                }
            });
        }

        // 11. Onboarding Journeys
        if (u.includes('/workforce/onboarding-journeys')) {
            return makeResponse([
                {
                    cohort: "2026-Q1 Cohort",
                    current_day: 25,
                    employee_name: "Amara Okonkwo",
                    role_title: "Frontend Engineer",
                    department: "Engineering",
                    status: "Ahead",
                    assigned_buddy: "Elena Rostova",
                    progress_pct: 65,
                    adaptive_notes: "Ahead of schedule. First PR merged on Day 12.",
                    tasks: mockState.tasks
                }
            ]);
        }

        // 12. Policy Query
        if (u.includes('/policy/query')) {
            return makeResponse({
                query: body.query || "",
                answer: "Per Policy POL-BEN-2025 (Section 4.2), employees are eligible for a $1,200 home workstation ergonomic stipend. Paid parental leave duration is 16 consecutive weeks at 100% base salary for all primary caregivers.",
                confidence: 95.0,
                citations: [
                    { document_title: "Employee Benefits & Stipend Handbook", policy_code: "POL-BEN-2025", page_number: 8, section_title: "Section 4.2 - Home Office & Ergonomics", retrieved_excerpt: "All full-time personnel receive a one-time $1,200 home workstation equipment stipend and 16 weeks of paid parental leave." }
                ],
                recommended_action: "Submit expense receipt to People Operations for immediate reimbursement."
            });
        }

        // 13. Governance Telemetry
        if (u.includes('/governance/mlops-telemetry')) {
            return makeResponse({ accuracy: 0.934, precision: 0.912, recall: 0.895, f1_score: 0.903, roc_auc: 0.962, avg_latency_ms: 2.1, device: "NVIDIA GeForce RTX 3070 Ti (CUDA)" });
        }
        if (u.includes('/governance/data-quality')) {
            return makeResponse({ data_quality_score: 99.4, validation_status: "Healthy", missing_values_pct: 0.0, duplicates_pct: 0.0, last_validated: "2026-09-13 18:00:00" });
        }
        if (u.includes('/governance/fairness-monitor')) {
            return makeResponse({ demographic_parity_score: 96.5, adverse_impact_ratio: 0.88, four_fifths_rule_status: "Compliant" });
        }

        // 14. Autonomous Agent Endpoints
        if (u.includes('/agent/status')) {
            return makeResponse({
                mode: mockState.agentMode,
                status: "Idle",
                last_patrol_time: "2026-09-13 18:00:00",
                total_messages_processed: 12,
                total_autonomous_actions: mockState.audit.length + 8,
                total_savings_secured_usd: 285000.0,
                sentinel_daemon: {
                    daemon_running: true,
                    tick_count: 42,
                    last_tick: new Date().toLocaleTimeString(),
                    overnight_actions_count: 6,
                    overnight_savings_usd: 192000.0
                }
            });
        }

        if (u.includes('/agent/mode')) {
            mockState.agentMode = body.mode || "Autonomous";
            return makeResponse({ success: true, current_mode: mockState.agentMode });
        }

        if (u.includes('/agent/briefing')) {
            return makeResponse({
                date: new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }),
                agent_name: "Atlas",
                tagline: "Your 24/7 Autonomous People Operations Partner",
                operating_mode: "Auto-Pilot (Fully Autonomous)",
                headline: "Good morning! Overnight, Atlas autonomously executed 4 workforce operations.",
                financial_savings_secured_usd: 192000.0,
                total_active_staff: 32,
                workforce_health_score: 88.4,
                critical_retention_risks: 3,
                cherrington_functions: [
                    { id: "staffing", name: "1. Staffing / Recruitment", operational_scope: "Talent Sourcing & Capacity Planning", status: "Optimal", score: 94 },
                    { id: "performance", name: "2. Performance Evaluation", operational_scope: "Performance Review & 9-Box Calibration", status: "Calibrated", score: 91 },
                    { id: "compensation", name: "3. Compensation & Equity", operational_scope: "Market Benchmark & Compa-Ratio Parity", status: "Balanced", score: 89 },
                    { id: "training", name: "4. Training & Development", operational_scope: "Upskilling Tracks & Leadership Mentoring", status: "Active", score: 92 },
                    { id: "relations", name: "5. Employee Relations", operational_scope: "Workplace Climate & Conflict Resolution", status: "Healthy", score: 95 },
                    { id: "safety", name: "6. Safety & Health", operational_scope: "Overtime Caps & Burnout Prevention", status: "Enforced", score: 86 },
                    { id: "research", name: "7. Workforce Research & Analytics", operational_scope: "Absenteeism & Delay Root-Cause Diagnostics", status: "Empirical", score: 96 }
                ],
                marthalia_benefits: [
                    { benefit: "Competent Talent Utilization", impact: "High skill-to-role matching index (94%)" },
                    { benefit: "Productivity Proportionality", impact: "Zero understaffed shifts in core engineering" },
                    { benefit: "Labor Needs Determination", impact: "Proactive 6-month capacity forecast established" },
                    { benefit: "Employment Information Handling", impact: "Centralized, zero-leakage employee records" },
                    { benefit: "Pre-Planning Research", impact: "Absenteeism root causes diagnosed prior to turnover" }
                ],
                strategic_recommendations: [
                    "Authorize Elena Rostova's +6% market retention package to permanently lock in core engineering architecture.",
                    "Review REQ-2025-01 top candidate Elena Rostova (92% blind match) for panel interview.",
                    "Verify Day 14 onboarding progress for newly provisioned cloud architect Kavita Sharma."
                ]
            });
        }

        if (u.includes('/agent/sentinel/status')) {
            return makeResponse({
                daemon_running: true,
                tick_count: 42,
                last_tick: new Date().toLocaleTimeString(),
                overnight_actions_count: 6,
                overnight_savings_usd: 192000.0
            });
        }

        if (u.includes('/agent/sentinel/tick')) {
            return makeResponse({
                tick_number: 43,
                timestamp: new Date().toLocaleTimeString(),
                findings: [
                    { function: "Safety & Health", status: "Optimal", autonomous_action: "Verified overtime below 15h/mo limits" },
                    { function: "Compensation", status: "Optimal", autonomous_action: "Compa-ratios aligned across bands" }
                ]
            });
        }

        if (u.includes('/agent/sentinel/research')) {
            return makeResponse({
                title: "Empirical Personnel Research & Absenteeism Analysis",
                academic_foundation: "Workforce Intelligence & Attendance Diagnostics",
                absenteeism_analysis: {
                    overall_absence_rate_pct: 2.4,
                    unplanned_absences_last_30d: 24,
                    root_causes: [
                        { cause: "Overtime Burnout Fatigue", contribution_pct: 58.0, description: "Staff logging >20h overtime show 4.2x higher absence rate.", intervention: "8h/mo overtime cap enforced." },
                        { cause: "Commute Distance (>40km)", contribution_pct: 24.0, description: "Staff commuting >40km report 3.1x higher late arrival delays.", intervention: "2-day flexible remote policy applied." },
                        { cause: "Dependent & Health Strains", contribution_pct: 18.0, description: "Unforeseen family responsibilities.", intervention: "Emergency backup care allowance." }
                    ]
                },
                recruitment_reasonableness_audit: {
                    procedure_rating: "High (92/100)",
                    average_time_to_hire_days: 18.4,
                    offer_acceptance_rate_pct: 91.2,
                    blind_screening_fairness_delta: "+16.8% diversity pass-through"
                },
                workforce_dissatisfaction_matrix: {
                    overall_satisfaction_score: 7.8,
                    dissatisfaction_drivers: [
                        { driver: "On-Call Pager Interruptions", impact_severity: "Critical", affected_roles: "DevOps & Cloud Systems" },
                        { driver: "Compensation Below Band Median", impact_severity: "High", affected_roles: "Senior Software Engineers" },
                        { driver: "Meeting Density > 20h/wk", impact_severity: "Moderate", affected_roles: "Product & Design" }
                    ]
                }
            });
        }

        if (u.includes('/agent/onboard-new-hire')) {
            const cleanName = (body.candidate_name || "Elena Rostova").trim();
            const parts = cleanName.toLowerCase().split(' ');
            const first = parts[0] || "new";
            const last = parts.length > 1 ? parts[parts.length - 1] : "hire";
            const corpEmail = `${first}.${last}@worksight.ai`;
            const ssoUser = `${first[0]}${last}`;
            const tempPass = `Welcome2026!${first.charAt(0).toUpperCase() + first.slice(1)}`;
            const role = body.role_title || "Senior Engineer";
            const dept = body.department || "Engineering";

            mockState.audit.unshift({
                id: Date.now(),
                timestamp: new Date().toLocaleTimeString(),
                event_type: "AutonomousOnboarding",
                actor: "Atlas Autonomous Agent",
                summary: `Autonomously provisioned ${corpEmail}, issued 6 cloud accounts, and dispatched MacBook Pro M3 Max for ${cleanName}.`,
                model_version: "Atlas-v2.4"
            });

            return makeResponse({
                status: "Success - Fully Automated",
                employee_name: cleanName,
                role_title: role,
                department: dept,
                corporate_email: corpEmail,
                sso_username: ssoUser,
                temporary_password: tempPass,
                hardware_and_stipend: {
                    primary_laptop: "Apple MacBook Pro 16-inch (Apple M3 Max, 36GB Unified Memory, 1TB SSD)",
                    home_office_stipend_usd: 1200.0,
                    dispatch_status: "Courier Dispatched (#WS-88392-US)"
                },
                assigned_buddy: dept === "Engineering" ? "Elena Rostova (Staff Systems Engineer)" : "Marcus Brody (Lead Product Partner)",
                dispatch_timestamp: new Date().toLocaleTimeString()
            });
        }

        if (u.includes('/agent/feed')) {
            return makeResponse([
                { id: "ACT-AUTO-1", timestamp: "2026-09-13 18:00:03", title: "Autonomous Onboarding: Kavita Sharma", summary: "Generated kavita.sharma@worksight.ai, provisioned 6 IT tools, authorized MacBook Pro M3 Max dispatch with $1,200 stipend.", savings_usd: 4200.0, status: "Executed" },
                { id: "ACT-AUTO-2", timestamp: "2026-09-13 17:48:10", title: "Workload Rebalancing: Elena Rostova", summary: "Capped overtime at 8h/mo, simulated counterfactual salary parity (+6%), reducing flight risk to 18.2%.", savings_usd: 72000.0, status: "Executed" },
                { id: "ACT-AUTO-3", timestamp: "2026-09-13 17:35:15", title: "Compensation Equity Calibration", summary: "Autonomously adjusted compa-ratio for Marcus Brody (+5.2%) per POL-COMP-2025.", savings_usd: 38000.0, status: "Executed" },
                { id: "ACT-AUTO-4", timestamp: "2026-09-13 17:15:30", title: "Blind Resume Screening for REQ-2025-01", summary: "Ranked 3 candidates with demographic anonymization. Identified Elena Rostova as top 92.4% match.", savings_usd: 15000.0, status: "Executed" }
            ]);
        }

        if (u.includes('/agent/message')) {
            const msg = (body.message || "").toLowerCase();
            
            if (msg.includes('briefing') || msg.includes('morning') || msg.includes('overnight') || msg.includes('summary')) {
                return makeResponse({
                    intent: "Executive Morning Briefing",
                    agent_response: "Good morning! Overnight, Atlas autonomously executed 4 workforce operations under Auto-Pilot mode.\n• Financial Impact: Secured $192,000 in prevented turnover costs.\n• Workforce Health Score: 88.4/100 across 32 active personnel.\n• Core Operations Status: Staffing (94%), Performance (91%), Compensation (89%), Training (92%), Relations (95%), Safety (86%), Research (96%).\n• Priority Recommendation: Authorize Elena Rostova's +6% market retention package to permanently lock in core engineering architecture."
                });
            }

            if (msg.includes('absenteeism') || msg.includes('delays') || msg.includes('dissatisfaction') || msg.includes('research')) {
                return makeResponse({
                    intent: "Personnel Research Analysis",
                    agent_response: "Based on workforce diagnostics and attendance analytics, I evaluated company absenteeism and dissatisfaction:\n1. Unplanned Absences: 24 incidents (Rate: 2.4%).\n2. Primary Root Cause: Overtime Burnout Fatigue (58% contribution). Staff logging >20h overtime have a 4.2x higher absence rate.\n3. Intervention: Automated 8h/mo overtime cap enforced.\n4. Recruitment Reasonableness: 92/100 with +16.8% diversity pass-through via blind screening.\n5. Friction Driver: On-call pager interruptions in DevOps & Cloud Systems."
                });
            }

            if (msg.includes('onboard') || msg.includes('provision') || msg.includes('mail')) {
                const candidateName = msg.includes('tariq') ? "Tariq Vance" : msg.includes('elena') ? "Elena Rostova" : "Kavita Sharma";
                const role = msg.includes('tariq') ? "Senior Infrastructure Architect" : "Senior Cloud Architect";
                const email = `${candidateName.toLowerCase().replace(' ', '.')}@worksight.ai`;
                return makeResponse({
                    intent: "Autonomous Onboarding & IT Provisioning",
                    agent_response: `I autonomously completed the full onboarding and IT provisioning pipeline for ${candidateName} (${role}):\n1. Company Email Generated: ${email}\n2. IT Accounts Active: Google Workspace, GitHub Enterprise, Slack (#engineering), Jira, Zero-Trust VPN\n3. Hardware Dispatched: Apple MacBook Pro 16-inch M3 Max with $1,200 home office stipend authorized\n4. 30-60-90 Day Roadmap Assigned: Paired with Elena Rostova (Staff Systems Engineer)\n5. Welcome Package & SSO Credentials dispatched to hire's inbox. Action recorded to audit log.`,
                    provisioning_result: {
                        corporate_email: email,
                        sso_username: candidateName.charAt(0).toLowerCase() + candidateName.split(' ')[1].toLowerCase(),
                        temporary_password: `Welcome2026!${candidateName.split(' ')[0]}`,
                        hardware_and_stipend: {
                            primary_laptop: "Apple MacBook Pro 16-inch (Apple M3 Max, 36GB, 1TB SSD)",
                            home_office_stipend_usd: 1200.0,
                            dispatch_status: "Courier Dispatched (#WS-88392-US)"
                        },
                        assigned_buddy: "Elena Rostova (Staff Systems Engineer)"
                    }
                });
            }

            if (msg.includes('patrol') || msg.includes('audit')) {
                return makeResponse({
                    intent: "Autonomous Organization Patrol",
                    agent_response: "I completed an autonomous organization patrol across 32 employees in 6 departments. Identified 3 workforce vulnerabilities. 2 interventions were processed in Autonomous mode, securing $126,000 in turnover replacement savings."
                });
            }

            if (msg.includes('elena') || msg.includes('burnout') || msg.includes('overtime')) {
                return makeResponse({
                    intent: "Retention Risk Mitigation",
                    agent_response: "I evaluated Elena Rostova's signals. Baseline flight risk was 78.4% due to 32.4 hrs/mo overtime and a compa-ratio below market. I ran a counterfactual simulation (-25% overtime, +6% compensation) and autonomously executed action #ACT-104. Projected flight risk drops to 18.2%, securing $72,000 in net annual ROI."
                });
            }

            return makeResponse({
                intent: "Workforce Cross-Source Analysis",
                agent_response: "Atlas evaluated workforce telemetry across all 6 monitored departments. Engineering and Product & Design are flagged for elevated flight risk. Recommended next step: review active retention packages in the HR Action Center."
            });
        }

        // Fallback to real fetch if unhandled
        return originalFetch.apply(this, arguments);
    };

    console.log("Atlas 24/7 Autonomous Client-Side Mock Provider active for GitHub Pages deployment.");
})();
