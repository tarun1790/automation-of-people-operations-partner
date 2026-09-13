// WorkSight AI - Enterprise Client Application Logic

const API_BASE = '/api/v1';

// App State
let currentTab = 'dashboard';
let anonymizeBias = false;
let skillGraphData = null;

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadDashboardSummary();
    loadRiskRadar();
    loadAIInsights();
    setupCommandCenter();
    setupWhatIfSimulator();
    loadHRActions();
    loadAuditTrail();
    loadAttritionPredictions();
    loadTalentIntelligence();
    loadPerformanceMatrix();
    loadSkillGraph();
    loadOnboardingJourneys();
    setupPolicyIntelligence();
    loadGovernanceTelemetry();
    loadAgentStatus();
    loadAgentFeed();
    loadExecutiveBriefing();

    // Live continuous sentinel polling
    setInterval(() => {
        loadExecutiveBriefing();
        loadAgentStatus();
        loadAgentFeed();
        loadDashboardSummary();
    }, 15000);
});

// Navigation Handling
function initNavigation() {
    const navButtons = document.querySelectorAll('.apple-segment-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });
}

function switchTab(tabId) {
    currentTab = tabId;
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    const target = document.getElementById(`tab-${tabId}`);
    if (target) target.classList.remove('hidden');

    document.querySelectorAll('.apple-segment-btn').forEach(btn => {
        if (btn.getAttribute('data-tab') === tabId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    if (tabId === 'skills') {
        setTimeout(renderSkillGraphCanvas, 50);
    } else if (tabId === 'agent') {
        loadAgentStatus();
        loadAgentFeed();
    }
}

// 1. Executive Summary
async function loadDashboardSummary() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/summary`);
        const data = await res.json();

        document.getElementById('metric-total-emps').textContent = data.total_employees;
        document.getElementById('metric-high-risk').textContent = data.high_risk_employees;
        document.getElementById('metric-health-index').textContent = `${data.workforce_health_score}/100`;
        document.getElementById('metric-avg-perf').textContent = `${data.average_performance} / 5.0`;
        document.getElementById('metric-open-pos').textContent = data.open_positions;
        document.getElementById('metric-skill-cov').textContent = `${data.skill_coverage_pct}%`;
        document.getElementById('metric-pending-actions').textContent = data.pending_actions_count;
        document.getElementById('metric-spofs').textContent = data.critical_spofs_count;
    } catch (err) {
        console.error('Failed to load dashboard summary:', err);
    }
}

// 2. Department Risk Status (Radar)
async function loadRiskRadar() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/risk-radar`);
        const data = await res.json();
        const container = document.getElementById('risk-radar-cards');
        if (!container) return;

        container.innerHTML = '';
        data.department_risk_matrix.forEach(dept => {
            const badgeClass = dept.risk_level === 'CRITICAL' ? 'apple-badge-red' :
                               dept.risk_level === 'HIGH' ? 'apple-badge-orange' :
                               dept.risk_level === 'MODERATE' ? 'apple-badge-blue' : 'apple-badge-green';

            const card = document.createElement('div');
            card.className = 'apple-card p-5 flex flex-col justify-between';
            card.innerHTML = `
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-semibold text-sm text-[#1d1d1f]">${dept.department}</span>
                        <span class="apple-badge ${badgeClass}">${dept.risk_level} RISK</span>
                    </div>
                    <div class="text-xs text-[#86868b] mb-1.5">
                        Staff: <strong class="text-[#1d1d1f]">${dept.headcount}</strong> • Turnover Risk: <strong class="${dept.risk_score >= 60 ? 'text-[#ff3b30]' : 'text-[#34c759]'}">${dept.risk_score}/100</strong>
                    </div>
                    <div class="text-[11px] text-[#86868b] mb-3 font-medium">
                        ${dept.risk_level === 'CRITICAL' ? '⚠️ Imminent flight threat due to overtime & pay gap' :
                          dept.risk_level === 'HIGH' ? '⚠️ Elevated burnout & flight probability' : '✓ Stable retention & healthy pace'}
                    </div>
                    <div class="space-y-1.5 mb-3 bg-[#f5f5f7] p-2.5 rounded-xl">
                        ${dept.detected_signals.map(s => `<div class="text-xs text-[#1d1d1f] flex items-start"><span class="text-[#ff9500] mr-1.5">•</span><span>${s}</span></div>`).join('')}
                    </div>
                </div>
                <div class="pt-3 border-t border-[rgba(0,0,0,0.06)] text-xs text-[#86868b] flex justify-between items-center">
                    <span>Overtime: <strong class="text-[#1d1d1f]">${dept.metrics.avg_overtime_hrs}h/mo</strong></span>
                    <button onclick="openSimulationForDept('${dept.department}')" class="text-[#0071e3] hover:underline font-medium">Simulate Fix →</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error('Failed to load risk radar:', err);
    }
}

// 3. Recommended Interventions (AI Insights)
async function loadAIInsights() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/insights`);
        const insights = await res.json();
        const container = document.getElementById('ai-insights-container');
        if (!container) return;

        container.innerHTML = '';
        insights.forEach(ins => {
            const card = document.createElement('div');
            card.className = 'apple-card p-5 flex flex-col justify-between';
            card.innerHTML = `
                <div>
                    <div class="flex justify-between items-start mb-1.5">
                        <span class="apple-badge apple-badge-blue">${ins.badge}</span>
                        <span class="text-[11px] text-[#86868b]">Confidence: ${ins.confidence}%</span>
                    </div>
                    <h4 class="text-sm font-semibold text-[#1d1d1f] mb-1">${ins.target}</h4>
                    <p class="text-xs text-[#86868b] mb-3 leading-relaxed">${ins.finding}</p>
                    <div class="bg-[#f5f5f7] p-3 rounded-xl mb-3 space-y-1">
                        <div class="text-[10px] font-semibold text-[#86868b] uppercase tracking-wider">Supporting Evidence:</div>
                        ${ins.evidence.map(e => `<div class="text-xs text-[#1d1d1f] flex items-start"><span class="text-[#0071e3] mr-1.5">•</span><span>${e}</span></div>`).join('')}
                    </div>
                    <div class="text-xs text-[#1d1d1f] mb-3 font-medium">
                        <strong class="text-[#86868b]">Action:</strong> ${ins.recommended_action}
                    </div>
                </div>
                <div class="flex gap-2 pt-3 border-t border-[rgba(0,0,0,0.06)]">
                    <button onclick="switchTab('actions')" class="apple-btn-primary flex-1 text-xs justify-center">Review Proposal</button>
                    <button onclick="switchTab('simulation')" class="apple-btn-secondary text-xs">Simulate Levers</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error('Failed to load insights:', err);
    }
}

// 4. HR Assistant & Natural Language Search
function setupCommandCenter() {
    const input = document.getElementById('command-input');
    const submitBtn = document.getElementById('command-submit-btn');
    if (!input || !submitBtn) return;

    submitBtn.addEventListener('click', () => runCommandQuery(input.value));
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') runCommandQuery(input.value);
    });

    document.querySelectorAll('.preset-cmd-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const query = btn.getAttribute('data-cmd');
            input.value = query;
            runCommandQuery(query);
        });
    });
}

async function runCommandQuery(query) {
    if (!query || !query.trim()) return;
    const outputArea = document.getElementById('command-output-area');
    outputArea.classList.remove('hidden');
    outputArea.innerHTML = `<div class="text-xs text-slate-500 py-3">Evaluating workforce records across departments...</div>`;

    try {
        const res = await fetch(`${API_BASE}/dashboard/command-center`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        const data = await res.json();

        outputArea.innerHTML = `
            <div class="card p-4 border border-blue-200 mt-2 space-y-2.5">
                <div class="flex justify-between items-center text-xs pb-2 border-b border-slate-100">
                    <span class="text-slate-600">Database Query: <strong>${data.tool_called}</strong></span>
                    <span class="badge badge-blue">Confidence: ${data.confidence}%</span>
                </div>
                <div>
                    <h4 class="text-xs font-bold text-slate-800 uppercase">Analysis & Findings:</h4>
                    <p class="text-xs text-slate-700 mt-0.5 leading-relaxed">${data.executive_summary}</p>
                </div>
                <div class="bg-slate-50 p-2.5 rounded border border-slate-200 text-xs">
                    <div class="font-semibold text-slate-600 mb-1">Supporting Records:</div>
                    <pre class="font-mono text-[11px] text-slate-700 whitespace-pre-wrap overflow-x-auto">${JSON.stringify(data.evidence, null, 2)}</pre>
                </div>
                <div class="p-2.5 bg-blue-50/60 rounded border border-blue-200 text-xs">
                    <span class="font-semibold text-blue-900">Recommended Action:</span>
                    <p class="text-slate-700 mt-0.5">${data.recommended_action}</p>
                    <div class="text-emerald-700 font-semibold mt-1">Expected Outcome: ${data.expected_impact}</div>
                </div>
            </div>
        `;
    } catch (err) {
        outputArea.innerHTML = `<div class="text-red-600 text-xs py-2">Error processing query: ${err.message}</div>`;
    }
}

// 5. Scenario & Budget Planner
function setupWhatIfSimulator() {
    const otSlider = document.getElementById('sim-overtime-slider');
    const salSlider = document.getElementById('sim-salary-slider');
    const promoSlider = document.getElementById('sim-promo-slider');
    const staffSlider = document.getElementById('sim-staff-slider');
    const deptSelect = document.getElementById('sim-dept-select');

    const otVal = document.getElementById('sim-overtime-val');
    const salVal = document.getElementById('sim-salary-val');
    const promoVal = document.getElementById('sim-promo-val');
    const staffVal = document.getElementById('sim-staff-val');

    const updateSimulation = async () => {
        otVal.textContent = `${otSlider.value}%`;
        salVal.textContent = `+${salSlider.value}%`;
        promoVal.textContent = `${promoSlider.value} mos`;
        staffVal.textContent = `+${staffSlider.value}`;

        try {
            const res = await fetch(`${API_BASE}/simulation/simulate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    department: deptSelect.value,
                    overtime_delta_pct: parseFloat(otSlider.value),
                    salary_delta_pct: parseFloat(salSlider.value),
                    promotion_acceleration_months: parseInt(promoSlider.value),
                    added_headcount: parseInt(staffSlider.value)
                })
            });
            const data = await res.json();
            renderSimulationResults(data);
        } catch (err) {
            console.error('Simulation error:', err);
        }
    };

    [otSlider, salSlider, promoSlider, staffSlider, deptSelect].forEach(el => {
        if (el) el.addEventListener('input', updateSimulation);
    });

    updateSimulation();
}

function openSimulationForDept(dept) {
    const deptSelect = document.getElementById('sim-dept-select');
    if (deptSelect) deptSelect.value = dept;
    switchTab('simulation');
    const otSlider = document.getElementById('sim-overtime-slider');
    if (otSlider) otSlider.dispatchEvent(new Event('input'));
}

function renderSimulationResults(data) {
    if (data.error) return;

    document.getElementById('sim-current-risk').textContent = `${data.current_state.attrition_risk_pct}%`;
    document.getElementById('sim-proj-risk').textContent = `${data.projected_state.attrition_risk_pct}%`;

    const imp = data.impact_analysis.estimated_improvement_pp;
    const impEl = document.getElementById('sim-risk-delta');
    impEl.textContent = `${imp >= 0 ? '-' : '+'}${Math.abs(imp)} pp`;
    impEl.className = imp >= 0 ? 'text-2xl font-bold text-emerald-700' : 'text-2xl font-bold text-red-700';

    document.getElementById('sim-prevented-departures').textContent = data.impact_analysis.departures_prevented_annually;
    document.getElementById('sim-turnover-savings').textContent = `$${data.impact_analysis.turnover_replacement_savings_usd.toLocaleString()}`;
    document.getElementById('sim-net-roi').textContent = `$${data.impact_analysis.net_annual_financial_benefit_usd.toLocaleString()}`;
    document.getElementById('sim-disclaimer').textContent = data.model_disclaimer;
}

// 6. HR Approvals & Action Center
async function loadHRActions() {
    try {
        const res = await fetch(`${API_BASE}/governance/actions`);
        const actions = await res.json();
        const container = document.getElementById('actions-table-body');
        if (!container) return;

        container.innerHTML = '';
        actions.forEach(act => {
            const row = document.createElement('tr');

            const badgeClass = act.status === 'Approved' ? 'badge-green' :
                               act.status === 'Executed' ? 'badge-blue' :
                               act.status === 'Rejected' ? 'badge-red' : 'badge-amber';

            row.innerHTML = `
                <td class="font-mono text-slate-500">ACT-${act.action_id}</td>
                <td class="font-semibold text-slate-900">${act.title}</td>
                <td>${act.target_entity}</td>
                <td><span class="badge ${act.priority === 'Critical' ? 'badge-red' : 'badge-amber'}">${act.priority}</span></td>
                <td class="max-w-xs truncate text-slate-600">${act.expected_impact}</td>
                <td><span class="badge ${badgeClass}">${act.status}</span></td>
                <td>
                    ${act.status === 'Pending Approval' ? `
                        <div class="flex gap-1.5">
                            <button onclick="reviewAction(${act.action_id}, 'Approved')" class="btn-success text-xs">Approve</button>
                            <button onclick="reviewAction(${act.action_id}, 'Rejected')" class="btn-danger text-xs">Dismiss</button>
                        </div>
                    ` : act.status === 'Approved' ? `
                        <button onclick="reviewAction(${act.action_id}, 'Executed')" class="btn-primary text-xs">Execute</button>
                    ` : `<span class="text-slate-400 text-xs">Recorded</span>`}
                </td>
            `;
            container.appendChild(row);
        });
    } catch (err) {
        console.error('Failed to load HR actions:', err);
    }
}

async function reviewAction(actionId, decision) {
    try {
        const res = await fetch(`${API_BASE}/governance/actions/${actionId}/review`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                decision,
                actor: 'Sarah Jenkins (HR Director)',
                notes: `Action updated to ${decision}.`
            })
        });
        const data = await res.json();
        if (data.success) {
            loadHRActions();
            loadAuditTrail();
            loadDashboardSummary();
        }
    } catch (err) {
        console.error('Error updating action:', err);
    }
}

// 7. Audit Trail
async function loadAuditTrail() {
    try {
        const res = await fetch(`${API_BASE}/governance/audit-trail?limit=15`);
        const logs = await res.json();
        const container = document.getElementById('audit-table-body');
        if (!container) return;

        container.innerHTML = '';
        logs.forEach(l => {
            const row = document.createElement('tr');
            row.className = 'text-xs';
            row.innerHTML = `
                <td class="text-slate-500 font-mono">${l.timestamp}</td>
                <td class="font-semibold text-slate-800">${l.event_type}</td>
                <td class="text-slate-600">${l.actor}</td>
                <td class="text-slate-700 max-w-sm truncate">${l.summary}</td>
                <td class="text-slate-400 font-mono">${l.model_version}</td>
            `;
            container.appendChild(row);
        });
    } catch (err) {
        console.error('Failed to load audit trail:', err);
    }
}

// 8. Employee Flight Risk & Retention Analysis
async function loadAttritionPredictions() {
    try {
        const res = await fetch(`${API_BASE}/workforce/attrition-predictions`);
        const preds = await res.json();
        const container = document.getElementById('attrition-table-body');
        if (!container) return;

        container.innerHTML = '';
        preds.forEach(p => {
            const row = document.createElement('tr');

            const badgeClass = p.risk_level === 'CRITICAL' ? 'badge-red' :
                               p.risk_level === 'HIGH' ? 'badge-amber' :
                               p.risk_level === 'MODERATE' ? 'badge-blue' : 'badge-green';

            row.innerHTML = `
                <td class="font-mono text-slate-500">${p.employee_code}</td>
                <td class="font-semibold text-slate-900">${p.employee_name}</td>
                <td>${p.department}</td>
                <td>${p.role_title}</td>
                <td class="font-bold text-slate-900">${(p.attrition_probability * 100).toFixed(1)}%</td>
                <td><span class="badge ${badgeClass}">${p.risk_level}</span></td>
                <td class="text-xs text-slate-700">
                    <div class="space-y-0.5">
                        ${p.top_contributing_factors.slice(0, 2).map(f => `<div><strong class="text-red-700 font-mono">${f.impact_pct}</strong> ${f.factor}</div>`).join('')}
                    </div>
                </td>
                <td class="text-xs text-slate-600 max-w-xs">${p.defensible_statement}</td>
            `;
            container.appendChild(row);
        });
    } catch (err) {
        console.error('Failed to load attrition predictions:', err);
    }
}

// 9. Recruitment & Interview Management
async function loadTalentIntelligence() {
    try {
        const reqRes = await fetch(`${API_BASE}/talent/postings`);
        const postings = await reqRes.json();
        const select = document.getElementById('talent-posting-select');
        if (!select || postings.length === 0) return;

        select.innerHTML = '';
        postings.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = `${p.req_code}: ${p.title} (${p.candidate_count} candidates)`;
            select.appendChild(opt);
        });

        const anonymizeToggle = document.getElementById('anonymize-toggle');
        if (anonymizeToggle) {
            anonymizeToggle.addEventListener('change', (e) => {
                anonymizeBias = e.target.checked;
                fetchCandidatesForPosting(select.value, anonymizeBias);
            });
        }

        select.addEventListener('change', () => fetchCandidatesForPosting(select.value, anonymizeBias));
        fetchCandidatesForPosting(postings[0].id, anonymizeBias);
        setupInterviewSimulator();
    } catch (err) {
        console.error('Failed to load postings:', err);
    }
}

async function fetchCandidatesForPosting(postingId, anonymize) {
    try {
        const res = await fetch(`${API_BASE}/talent/candidates/${postingId}?anonymize=${anonymize}`);
        const candidates = await res.json();
        const container = document.getElementById('candidates-rank-cards');
        if (!container) return;

        container.innerHTML = '';
        candidates.forEach((c, idx) => {
            const badgeClass = c.recommendation === 'Strong Hire' ? 'badge-green' :
                               c.recommendation === 'Consider' ? 'badge-amber' : 'badge-red';

            const card = document.createElement('div');
            card.className = 'card p-4 flex flex-col justify-between';
            card.innerHTML = `
                <div>
                    <div class="flex justify-between items-start mb-1.5">
                        <span class="text-xs text-slate-500 font-semibold">Rank #${idx + 1}</span>
                        <span class="badge ${badgeClass}">${c.recommendation}</span>
                    </div>
                    <h4 class="text-sm font-bold text-slate-900 mb-0.5">${c.full_name}</h4>
                    <div class="text-xs text-slate-500 mb-2">${c.current_title || 'Applicant'} | Exp: ${c.years_of_experience} yrs</div>
                    
                    <div class="grid grid-cols-2 gap-2 bg-slate-50 p-2.5 rounded border border-slate-200 text-xs mb-3">
                        <div>Skill Match: <strong class="text-slate-800">${c.skill_match_pct}%</strong></div>
                        <div>Experience Align: <strong class="text-slate-800">${c.experience_alignment_pct}%</strong></div>
                        <div class="col-span-2 pt-1 border-t border-slate-200">Composite Score: <strong class="text-emerald-700 text-sm font-bold">${c.composite_score}%</strong></div>
                    </div>

                    <div class="text-xs mb-2">
                        <span class="text-slate-500 font-semibold">Matched Skills:</span>
                        <div class="text-slate-700 flex flex-wrap gap-1 mt-1">
                            ${c.key_strengths.map(s => `<span class="bg-slate-100 text-slate-700 border border-slate-200 px-1.5 py-0.5 rounded text-[11px]">${s}</span>`).join('')}
                        </div>
                    </div>

                    ${c.skill_gaps.length > 0 ? `
                        <div class="text-xs mb-3">
                            <span class="text-red-600 font-semibold">Missing Skills:</span>
                            <div class="text-slate-700 flex flex-wrap gap-1 mt-1">
                                ${c.skill_gaps.map(g => `<span class="bg-red-50 text-red-700 border border-red-200 px-1.5 py-0.5 rounded text-[11px]">${g}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
                <div class="pt-2 border-t border-slate-100 text-xs text-slate-500 flex justify-between items-center">
                    <span>Stage: <strong>${c.stage}</strong></span>
                    <button onclick="prefillInterviewCandidate('${c.full_name}')" class="text-blue-700 hover:underline font-medium">Evaluate in Interview →</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error('Failed to fetch candidates:', err);
    }
}

// 10. Interview Intelligence Simulator
function setupInterviewSimulator() {
    const roleInput = document.getElementById('interview-role-input');
    const genBtn = document.getElementById('interview-gen-btn');
    const questionsSelect = document.getElementById('interview-questions-select');
    const criteriaBox = document.getElementById('interview-criteria-display');
    const answerInput = document.getElementById('interview-answer-input');
    const evalBtn = document.getElementById('interview-eval-btn');
    const scorecardArea = document.getElementById('interview-scorecard-area');

    if (!genBtn || !evalBtn) return;

    let loadedQuestions = [];

    genBtn.addEventListener('click', async () => {
        const role = roleInput.value || 'Senior Distributed Systems Engineer';
        genBtn.disabled = true;
        genBtn.textContent = 'Generating...';

        try {
            const res = await fetch(`${API_BASE}/talent/interviews/generate-questions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    role_title: role,
                    required_skills: ['Kubernetes', 'Go', 'Distributed Tracing', 'Kafka']
                })
            });
            loadedQuestions = await res.json();
            questionsSelect.innerHTML = '';
            loadedQuestions.forEach((q, idx) => {
                const opt = document.createElement('option');
                opt.value = idx;
                opt.textContent = `Q${idx + 1} (${q.category}): ${q.question.substring(0, 80)}...`;
                questionsSelect.appendChild(opt);
            });
            criteriaBox.textContent = loadedQuestions[0].criteria;
        } catch (err) {
            console.error('Error generating questions:', err);
        } finally {
            genBtn.disabled = false;
            genBtn.textContent = 'Generate Interview Questions';
        }
    });

    questionsSelect.addEventListener('change', () => {
        const q = loadedQuestions[questionsSelect.value];
        if (q) criteriaBox.textContent = q.criteria;
    });

    const fillStrongBtn = document.getElementById('fill-strong-answer');
    const fillWeakBtn = document.getElementById('fill-weak-answer');

    if (fillStrongBtn) {
        fillStrongBtn.addEventListener('click', () => {
            answerInput.value = "In my previous role at CloudScale, our production Kafka cluster suffered a severe latency spike. I investigated distributed traces using Jaeger and identified unindexed writes causing thread pool exhaustion. I reconfigured consumer partition limits, implemented an asynchronous batching buffer, and validated that p99 latency dropped by 85% within 2 hours.";
        });
    }

    if (fillWeakBtn) {
        fillWeakBtn.addEventListener('click', () => {
            answerInput.value = "We had a latency issue once. I told the team to restart the service and everything seemed fine after that.";
        });
    }

    evalBtn.addEventListener('click', async () => {
        const q = loadedQuestions[questionsSelect.value] || {
            question: "How do you diagnose distributed system latency spikes?",
            criteria: "Expects STAR method, metrics, profiling tools, and quantifiable outcome."
        };

        evalBtn.disabled = true;
        evalBtn.textContent = 'Analyzing...';

        try {
            const res = await fetch(`${API_BASE}/talent/interviews/evaluate-answer`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    role_title: roleInput.value,
                    question_text: q.question,
                    criteria: q.criteria,
                    candidate_answer: answerInput.value
                })
            });
            const evalData = await res.json();

            scorecardArea.classList.remove('hidden');
            scorecardArea.innerHTML = `
                <div class="card p-4 border border-blue-200 mt-3 space-y-3">
                    <div class="flex justify-between items-center pb-2 border-b border-slate-200">
                        <span class="text-xs font-bold uppercase text-slate-800 tracking-wider">Interview Evaluation Scorecard</span>
                        <span class="badge ${evalData.signal === 'Strong Hire' ? 'badge-green' : 'badge-red'} font-bold">${evalData.signal}</span>
                    </div>

                    <div class="grid grid-cols-4 gap-2 text-center bg-slate-50 p-3 rounded border border-slate-200">
                        <div>
                            <div class="text-[11px] text-slate-500">Technical Depth</div>
                            <div class="text-base font-bold text-slate-900">${evalData.technical_correctness_score}%</div>
                        </div>
                        <div>
                            <div class="text-[11px] text-slate-500">STAR Structure</div>
                            <div class="text-base font-bold text-slate-900">${evalData.star_structure_score}%</div>
                        </div>
                        <div>
                            <div class="text-[11px] text-slate-500">Relevance</div>
                            <div class="text-base font-bold text-slate-900">${evalData.relevance_score}%</div>
                        </div>
                        <div>
                            <div class="text-[11px] text-slate-500">Composite Score</div>
                            <div class="text-base font-bold text-emerald-700">${evalData.overall_score}%</div>
                        </div>
                    </div>

                    <div class="text-xs text-slate-800">
                        <span class="font-semibold text-emerald-800">Strengths:</span>
                        <ul class="list-disc list-inside mt-0.5 text-slate-700">
                            ${evalData.strengths.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="text-xs text-slate-800">
                        <span class="font-semibold text-red-700">Missing Elements:</span>
                        <ul class="list-disc list-inside mt-0.5 text-slate-700">
                            ${evalData.missing_aspects.map(m => `<li>${m}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="bg-slate-50 p-2.5 rounded border border-slate-200 text-xs">
                        <span class="font-semibold text-slate-800">Suggested Follow-Up Question:</span>
                        <p class="text-slate-700 italic mt-0.5">"${evalData.suggested_follow_up}"</p>
                    </div>
                </div>
            `;
        } catch (err) {
            scorecardArea.innerHTML = `<div class="text-red-600 text-xs">Evaluation error: ${err.message}</div>`;
        } finally {
            evalBtn.disabled = false;
            evalBtn.textContent = 'Score Candidate Answer';
        }
    });
}

function prefillInterviewCandidate(name) {
    switchTab('talent');
    const answerInput = document.getElementById('interview-answer-input');
    if (answerInput) answerInput.scrollIntoView({ behavior: 'smooth' });
}

// 11. Performance Intelligence & 9-Box Matrix
async function loadPerformanceMatrix() {
    try {
        const res = await fetch(`${API_BASE}/workforce/performance-matrix`);
        const data = await res.json();

        document.getElementById('perf-avg-score').textContent = `${data.average_performance} / 5.0`;
        document.getElementById('perf-hipo-count').textContent = data.high_potential_count;
        document.getElementById('perf-coaching-count').textContent = data.growth_coaching_needed_count;

        const cells = document.querySelectorAll('.formal-box-cell');
        cells.forEach(cell => {
            const quadName = cell.getAttribute('data-quadrant');
            const count = data.quadrant_distribution[quadName] || 0;
            const badge = cell.querySelector('.cell-count');
            if (badge) badge.textContent = `${count} emps`;

            cell.addEventListener('click', () => {
                filterPerformanceTable(data.matrix_items, quadName);
            });
        });

        renderPerformanceTable(data.matrix_items);
    } catch (err) {
        console.error('Failed to load performance matrix:', err);
    }
}

function renderPerformanceTable(items) {
    const container = document.getElementById('perf-table-body');
    if (!container) return;

    container.innerHTML = '';
    items.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="font-semibold text-slate-900">${item.employee_name}</td>
            <td>${item.department}</td>
            <td>${item.role_title}</td>
            <td class="font-bold text-slate-900">${item.performance_score}</td>
            <td><span class="badge badge-slate">${item.quadrant_name}</span></td>
            <td class="font-bold text-emerald-700">${item.promotion_readiness_score}%</td>
            <td class="text-xs text-slate-600 max-w-xs truncate">${item.recommended_path}</td>
        `;
        container.appendChild(row);
    });
}

function filterPerformanceTable(allItems, quadrantName) {
    const filtered = allItems.filter(i => i.quadrant_name === quadrantName);
    renderPerformanceTable(filtered);
}

// 12. Workforce Skill Graph Canvas & Mobility Pathfinder
async function loadSkillGraph() {
    try {
        const res = await fetch(`${API_BASE}/workforce/skills-graph`);
        skillGraphData = await res.json();

        // Single Point of Failure (SPOF) Alerts
        const spofContainer = document.getElementById('spof-alerts-container');
        if (spofContainer) {
            spofContainer.innerHTML = '';
            skillGraphData.critical_single_points_of_failure.forEach(s => {
                const alertCard = document.createElement('div');
                alertCard.className = 'p-2.5 bg-red-50 rounded border border-red-200 text-xs space-y-1';
                alertCard.innerHTML = `
                    <div class="flex justify-between items-center">
                        <strong class="text-red-800 font-bold">${s.skill_name}</strong>
                        <span class="badge badge-red">1 Person Holds</span>
                    </div>
                    <div class="text-slate-700">Held solely by <strong>${s.holder_name}</strong> (${s.holder_department}).</div>
                    <div class="text-slate-600 text-[11px]"><strong>Action:</strong> ${s.mitigation_plan}</div>
                `;
                spofContainer.appendChild(alertCard);
            });
        }

        // Department Skill Coverage
        const deptCovContainer = document.getElementById('dept-coverage-bars');
        if (deptCovContainer) {
            deptCovContainer.innerHTML = '';
            Object.entries(skillGraphData.department_skill_coverage).forEach(([dept, cov]) => {
                const bar = document.createElement('div');
                bar.className = 'text-xs space-y-1';
                bar.innerHTML = `
                    <div class="flex justify-between text-slate-700">
                        <span>${dept}</span>
                        <span class="font-bold">${cov}%</span>
                    </div>
                    <div class="w-full bg-slate-200 h-2 rounded overflow-hidden">
                        <div class="bg-blue-700 h-full rounded" style="width: ${cov}%;"></div>
                    </div>
                `;
                deptCovContainer.appendChild(bar);
            });
        }

        setupMobilityPathfinder();
    } catch (err) {
        console.error('Failed to load skill graph:', err);
    }
}

function renderSkillGraphCanvas() {
    const canvas = document.getElementById('skillCanvas');
    if (!canvas || !skillGraphData) return;
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = 440;

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const skillNodes = skillGraphData.nodes.filter(n => n.type === 'skill').slice(0, 14);
    const empNodes = skillGraphData.nodes.filter(n => n.type === 'employee').slice(0, 10);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) * 0.38;

    skillNodes.forEach((s, i) => {
        const angle = (i / skillNodes.length) * 2 * Math.PI;
        s.x = centerX + radius * Math.cos(angle);
        s.y = centerY + radius * Math.sin(angle);
    });

    const innerRadius = radius * 0.45;
    empNodes.forEach((e, i) => {
        const angle = (i / empNodes.length) * 2 * Math.PI;
        e.x = centerX + innerRadius * Math.cos(angle);
        e.y = centerY + innerRadius * Math.sin(angle);
    });

    // Draw Links
    ctx.lineWidth = 1;
    skillGraphData.links.slice(0, 35).forEach(l => {
        const sourceNode = empNodes.find(n => n.id === l.source);
        const targetNode = skillNodes.find(n => n.id === l.target);
        if (sourceNode && targetNode) {
            ctx.strokeStyle = '#cbd5e1';
            ctx.beginPath();
            ctx.moveTo(sourceNode.x, sourceNode.y);
            ctx.lineTo(targetNode.x, targetNode.y);
            ctx.stroke();
        }
    });

    // Draw Skill Nodes
    skillNodes.forEach(s => {
        const isSPOF = skillGraphData.critical_single_points_of_failure.some(sp => sp.skill_name === s.label);
        ctx.fillStyle = isSPOF ? '#dc2626' : '#2563eb';
        ctx.beginPath();
        ctx.arc(s.x, s.y, isSPOF ? 7 : 5, 0, 2 * Math.PI);
        ctx.fill();

        ctx.fillStyle = '#1e293b';
        ctx.font = '11px -apple-system, sans-serif';
        ctx.textAlign = s.x > centerX ? 'left' : 'right';
        ctx.fillText(s.label, s.x > centerX ? s.x + 9 : s.x - 9, s.y + 3);
    });

    // Draw Employee Nodes
    empNodes.forEach(e => {
        ctx.fillStyle = '#15803d';
        ctx.beginPath();
        ctx.arc(e.x, e.y, 6, 0, 2 * Math.PI);
        ctx.fill();

        ctx.fillStyle = '#0f172a';
        ctx.font = 'bold 11px -apple-system, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(e.label.split(' ')[0], e.x, e.y - 9);
    });
}

function setupMobilityPathfinder() {
    const btn = document.getElementById('calc-mobility-btn');
    const roleSelect = document.getElementById('mobility-target-role');
    const resultArea = document.getElementById('mobility-result-area');
    if (!btn) return;

    btn.addEventListener('click', async () => {
        btn.disabled = true;
        btn.textContent = 'Calculating...';

        try {
            const res = await fetch(`${API_BASE}/workforce/mobility-path`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    employee_id: 1, // Elena Rostova
                    target_role: roleSelect.value
                })
            });
            const data = await res.json();
            resultArea.classList.remove('hidden');
            resultArea.innerHTML = `
                <div class="card p-4 border border-blue-200 space-y-2.5 mt-3">
                    <div class="flex justify-between items-center text-xs pb-2 border-b border-slate-200">
                        <span class="text-slate-700">Target Role: <strong>${data.target_role}</strong></span>
                        <span class="badge badge-green font-bold">Readiness: ${data.readiness_pct}%</span>
                    </div>
                    <div class="text-xs">
                        <div class="font-semibold text-slate-800 mb-1">Competencies Already Met:</div>
                        <div class="flex flex-wrap gap-1">
                            ${data.matched_competencies.map(m => `<span class="bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded text-[11px]">${m.skill} (${m.current_proficiency})</span>`).join('')}
                        </div>
                    </div>
                    <div class="text-xs">
                        <div class="font-semibold text-slate-800 mb-1">Recommended Training & Certifications:</div>
                        <div class="space-y-1 text-slate-700">
                            ${data.missing_competencies.map(m => `<div class="flex items-center gap-1.5"><span class="text-blue-700">•</span><span><strong>${m.skill}:</strong> ${m.recommended_course}</span></div>`).join('')}
                        </div>
                    </div>
                    <div class="text-xs text-slate-600 pt-1 border-t border-slate-200">
                        Estimated Preparation Time: <strong>${data.estimated_readiness_timeline}</strong>
                    </div>
                </div>
            `;
        } catch (err) {
            console.error('Mobility error:', err);
        } finally {
            btn.disabled = false;
            btn.textContent = 'Calculate Training Path & Readiness';
        }
    });
}

// 13. New Hire Onboarding
async function loadOnboardingJourneys() {
    try {
        const res = await fetch(`${API_BASE}/workforce/onboarding-journeys`);
        const journeys = await res.json();
        const container = document.getElementById('onboarding-cards-container');
        if (!container) return;

        container.innerHTML = '';
        journeys.forEach(j => {
            const card = document.createElement('div');
            card.className = 'card p-5 space-y-3';
            card.innerHTML = `
                <div class="flex justify-between items-start pb-2 border-b border-slate-200">
                    <div>
                        <div class="text-xs text-slate-500 font-mono">${j.cohort} • Day ${j.current_day} of 90</div>
                        <h4 class="text-base font-bold text-slate-900">${j.employee_name}</h4>
                        <div class="text-xs text-blue-700 font-medium">${j.role_title} (${j.department})</div>
                    </div>
                    <div class="text-right">
                        <span class="badge ${j.status === 'Ahead' ? 'badge-green' : j.status === 'AtRisk' ? 'badge-red' : 'badge-blue'}">${j.status}</span>
                        <div class="text-xs text-slate-500 mt-1">Buddy: <strong>${j.assigned_buddy}</strong></div>
                    </div>
                </div>

                <div>
                    <div class="flex justify-between text-xs text-slate-600 mb-1">
                        <span>Milestone Progress</span>
                        <span class="font-bold text-blue-700">${j.progress_pct}%</span>
                    </div>
                    <div class="w-full bg-slate-200 h-2.5 rounded overflow-hidden">
                        <div class="bg-blue-700 h-full rounded" style="width: ${j.progress_pct}%;"></div>
                    </div>
                </div>

                <div class="text-xs text-slate-700 bg-slate-50 p-2.5 rounded border border-slate-200">
                    <strong>Pacing Notes:</strong> ${j.adaptive_notes || 'Progressing normally.'}
                </div>

                <div class="space-y-1.5">
                    <div class="text-xs font-semibold text-slate-700">Checklist Items:</div>
                    ${j.tasks.map(t => `
                        <div class="flex items-start gap-2 text-xs text-slate-800 p-2 bg-slate-50 rounded border border-slate-200">
                            <input type="checkbox" ${t.is_completed ? 'checked' : ''} onchange="toggleTask(${t.id}, this.checked)" class="mt-0.5 rounded border-slate-300 text-blue-700">
                            <div class="flex-1">
                                <div class="${t.is_completed ? 'line-through text-slate-400' : 'font-medium'}">${t.task_name}</div>
                                <div class="text-[11px] text-slate-500">${t.milestone_phase} • ${t.category}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error('Failed to load onboarding:', err);
    }
}

async function toggleTask(taskId, isCompleted) {
    try {
        await fetch(`${API_BASE}/workforce/onboarding/task-toggle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: taskId, is_completed: isCompleted })
        });
        loadOnboardingJourneys();
    } catch (err) {
        console.error('Failed to toggle task:', err);
    }
}

// 14. Policy Handbook Search
function setupPolicyIntelligence() {
    const input = document.getElementById('policy-search-input');
    const btn = document.getElementById('policy-search-btn');
    const resultArea = document.getElementById('policy-results-area');
    if (!btn || !input) return;

    const runPolicyQuery = async (q) => {
        if (!q.trim()) return;
        btn.disabled = true;
        btn.textContent = 'Searching...';

        try {
            const res = await fetch(`${API_BASE}/policy/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: q })
            });
            const data = await res.json();
            resultArea.classList.remove('hidden');

            resultArea.innerHTML = `
                <div class="card p-4 border border-blue-200 space-y-3 mt-3">
                    <div class="flex justify-between items-center pb-2 border-b border-slate-200 text-xs">
                        <span class="text-xs font-bold uppercase text-slate-800">Handbook Search Result</span>
                        <span class="badge badge-blue">Relevance: ${data.confidence}%</span>
                    </div>

                    <div class="text-xs text-slate-800 leading-relaxed">${data.answer.replace(/\n/g, '<br/>')}</div>

                    ${data.citations && data.citations.length > 0 ? `
                        <div class="bg-slate-50 p-3 rounded border border-slate-200 text-xs space-y-2">
                            <div class="font-semibold text-slate-700">Official Policy Reference:</div>
                            ${data.citations.map(c => `
                                <div class="p-2 bg-white rounded border border-slate-200">
                                    <div class="flex justify-between text-blue-800 font-semibold text-[11px] mb-1">
                                        <span>${c.document_title} (${c.policy_code})</span>
                                        <span>Page ${c.page_number} • ${c.section_title}</span>
                                    </div>
                                    <div class="text-slate-600 italic">"${c.retrieved_excerpt}"</div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}

                    <div class="text-xs text-slate-700 pt-1">
                        <strong>Standard Next Step:</strong> ${data.recommended_action || 'Consult People Partner'}
                    </div>
                </div>
            `;
        } catch (err) {
            resultArea.innerHTML = `<div class="text-red-600 text-xs">Search error: ${err.message}</div>`;
        } finally {
            btn.disabled = false;
            btn.textContent = 'Search Policies';
        }
    };

    btn.addEventListener('click', () => runPolicyQuery(input.value));
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') runPolicyQuery(input.value);
    });

    document.querySelectorAll('.preset-policy-btn').forEach(b => {
        b.addEventListener('click', () => {
            const q = b.getAttribute('data-query');
            input.value = q;
            runPolicyQuery(q);
        });
    });
}

// 15. Governance, Data Quality & Compliance
async function loadGovernanceTelemetry() {
    try {
        const mlRes = await fetch(`${API_BASE}/governance/mlops-telemetry`);
        const mlData = await mlRes.json();
        document.getElementById('mlops-accuracy').textContent = `${(mlData.accuracy * 100).toFixed(1)}%`;
        document.getElementById('mlops-precision').textContent = `${(mlData.precision * 100).toFixed(1)}%`;
        document.getElementById('mlops-recall').textContent = `${(mlData.recall * 100).toFixed(1)}%`;
        document.getElementById('mlops-f1').textContent = `${(mlData.f1_score * 100).toFixed(1)}%`;
        document.getElementById('mlops-roc-auc').textContent = mlData.roc_auc.toFixed(3);
        document.getElementById('mlops-latency').textContent = `${mlData.avg_latency_ms} ms`;
        document.getElementById('mlops-device').textContent = mlData.device;

        const dqRes = await fetch(`${API_BASE}/governance/data-quality`);
        const dqData = await dqRes.json();
        document.getElementById('dq-score').textContent = `${dqData.data_quality_score}%`;
        document.getElementById('dq-status').textContent = dqData.validation_status;
        document.getElementById('dq-missing').textContent = `${dqData.missing_values_pct}%`;
        document.getElementById('dq-duplicates').textContent = `${dqData.duplicates_pct}%`;
        document.getElementById('dq-last-check').textContent = dqData.last_validated;

        const fairRes = await fetch(`${API_BASE}/governance/fairness-monitor`);
        const fairData = await fairRes.json();
        document.getElementById('fair-parity-score').textContent = `${fairData.demographic_parity_score}/100`;
        document.getElementById('fair-adverse-ratio').textContent = fairData.adverse_impact_ratio;
        document.getElementById('fair-status').textContent = fairData.four_fifths_rule_status;
    } catch (err) {
        console.error('Failed to load governance telemetry:', err);
    }
}

// 16. Atlas Autonomous Agent Operations
let agentState = {
    mode: "Autonomous",
    status: "Idle",
    messages: [
        {
            sender: "Atlas Autonomous Agent",
            role: "agent",
            timestamp: "Just now",
            text: "Hello Sarah. I am Atlas, your 24/7 autonomous people operations partner. I continuously evaluate turnover risk across our 32 employees, auto-provision corporate email & IT access for new hires, and rebalance burnout schedules. How can I assist you right now?"
        }
    ]
};

async function loadAgentStatus() {
    try {
        const res = await fetch(`${API_BASE}/agent/status`);
        const data = await res.json();
        agentState.mode = data.mode;
        agentState.status = data.status;

        // Update UI pills & badges
        const dot = document.getElementById('header-agent-dot');
        const text = document.getElementById('header-agent-text');
        const deckBadge = document.getElementById('agent-deck-badge');
        const deckMode = document.getElementById('deck-agent-mode');
        const toggleBtn = document.getElementById('agent-mode-toggle-btn');
        const tasksCount = document.getElementById('deck-tasks-count');
        const savingsSecured = document.getElementById('deck-savings-secured');
        const lastPatrol = document.getElementById('deck-last-patrol');

        const isAuto = data.mode === "Autonomous";

        if (dot) dot.className = isAuto ? 'h-2 w-2 rounded-full bg-[#34c759] animate-pulse' : 'h-2 w-2 rounded-full bg-[#ff9500]';
        if (text) text.textContent = isAuto ? 'Auto-Pilot: Active' : 'Supervised: Human Review';
        if (deckBadge) {
            deckBadge.className = isAuto ? 'apple-badge apple-badge-green' : 'apple-badge apple-badge-orange';
            deckBadge.textContent = isAuto ? 'Auto-Pilot: Active' : 'Supervised Mode';
        }
        if (deckMode) deckMode.textContent = data.mode;
        if (toggleBtn) toggleBtn.textContent = isAuto ? 'Switch to Supervised Mode' : 'Switch to Autonomous Mode';
        if (tasksCount) tasksCount.textContent = data.total_autonomous_actions || 14;
        if (savingsSecured) savingsSecured.textContent = `$${(data.total_savings_secured_usd || 245000).toLocaleString()}`;
        if (lastPatrol) lastPatrol.textContent = data.last_patrol_time ? data.last_patrol_time.split(' ')[1] : 'Active';

    } catch (err) {
        console.error('Failed to load agent status:', err);
    }
}

async function toggleAgentMode() {
    const newMode = agentState.mode === "Autonomous" ? "Supervised" : "Autonomous";
    try {
        const res = await fetch(`${API_BASE}/agent/mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: newMode })
        });
        const data = await res.json();
        if (data.success) {
            agentState.mode = newMode;
            loadAgentStatus();
            loadAgentFeed();
        }
    } catch (err) {
        console.error('Failed to toggle agent mode:', err);
    }
}

async function loadAgentFeed() {
    try {
        const res = await fetch(`${API_BASE}/agent/feed`);
        const items = await res.json();
        const container = document.getElementById('agent-live-feed');
        if (!container) return;

        container.innerHTML = '';
        items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'p-3.5 bg-[#f5f5f7] rounded-2xl space-y-1.5 text-xs';
            card.innerHTML = `
                <div class="flex justify-between items-center text-[#86868b]">
                    <span class="font-mono text-[10px]">${item.timestamp.split(' ')[1] || item.timestamp}</span>
                    <span class="apple-badge ${item.status === 'Executed' ? 'apple-badge-green' : 'apple-badge-blue'} text-[10px]">${item.status}</span>
                </div>
                <div class="font-semibold text-[#1d1d1f] text-xs">${item.title}</div>
                <div class="text-[#86868b] leading-relaxed text-[11px]">${item.summary}</div>
                ${item.savings_usd > 0 ? `
                    <div class="text-[#34c759] font-medium text-[11px] pt-1 border-t border-[rgba(0,0,0,0.05)]">
                        + $${item.savings_usd.toLocaleString()} turnover savings secured
                    </div>
                ` : ''}
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error('Failed to load agent feed:', err);
    }
}

function renderChatStream() {
    const container = document.getElementById('agent-chat-stream');
    if (!container) return;

    container.innerHTML = '';
    agentState.messages.forEach(msg => {
        const isAgent = msg.role === 'agent';
        const el = document.createElement('div');
        el.className = `flex gap-3 ${isAgent ? '' : 'justify-end'}`;

        if (isAgent) {
            el.innerHTML = `
                <div class="h-7 w-7 rounded-full bg-[#1d1d1f] flex items-center justify-center text-white text-xs font-semibold shrink-0 mt-0.5">A</div>
                <div class="bg-white border border-[rgba(0,0,0,0.06)] p-3.5 rounded-2xl rounded-tl-sm text-xs space-y-2 shadow-sm max-w-xl text-[#1d1d1f]">
                    <div class="flex justify-between items-center text-[#86868b] text-[10px]">
                        <span>${msg.sender}</span>
                        <span>${msg.timestamp}</span>
                    </div>
                    <div class="leading-relaxed whitespace-pre-wrap">${msg.text}</div>
                    ${msg.prov ? `
                        <div class="bg-[#f0f7ff] p-3 rounded-xl border border-[#0071e3]/15 space-y-1.5 text-[11px]">
                            <div class="font-semibold text-[#0071e3]">Autonomous Provisioning Credentials:</div>
                            <div>• Corporate Email: <strong>${msg.prov.corporate_email}</strong></div>
                            <div>• SSO Login: <strong>${msg.prov.sso_username}</strong> (Temp: ${msg.prov.temporary_password})</div>
                            <div>• Hardware: ${msg.prov.hardware_and_stipend.primary_laptop}</div>
                            <div>• Ergonomic Stipend: $${msg.prov.hardware_and_stipend.home_office_stipend_usd}</div>
                            <div>• Assigned Buddy: ${msg.prov.assigned_buddy}</div>
                        </div>
                    ` : ''}
                </div>
            `;
        } else {
            el.innerHTML = `
                <div class="bg-[#0071e3] text-white p-3.5 rounded-2xl rounded-tr-sm text-xs shadow-sm max-w-xl">
                    <div class="text-[10px] text-white/80 mb-0.5 text-right">${msg.timestamp}</div>
                    <div class="leading-relaxed whitespace-pre-wrap">${msg.text}</div>
                </div>
            `;
        }
        container.appendChild(el);
    });

    container.scrollTop = container.scrollHeight;
}

async function sendAgentMessage(text) {
    if (!text || !text.trim()) return;

    const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    agentState.messages.push({
        sender: "Sarah Jenkins",
        role: "user",
        timestamp: timeNow,
        text: text
    });
    renderChatStream();

    try {
        const res = await fetch(`${API_BASE}/agent/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sender: "Sarah Jenkins (HR Director)",
                message: text,
                channel: "Atlas Console"
            })
        });
        const data = await res.json();

        agentState.messages.push({
            sender: "Atlas Autonomous Agent",
            role: "agent",
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            text: data.agent_response,
            prov: data.provisioning_result
        });
        renderChatStream();
        loadAgentStatus();
        loadAgentFeed();
        loadDashboardSummary();
        loadRiskRadar();
        loadHRActions();
        loadAuditTrail();
    } catch (err) {
        console.error('Agent message error:', err);
    }
}

function submitAgentChat() {
    const input = document.getElementById('agent-message-input');
    if (input && input.value) {
        sendAgentMessage(input.value);
        input.value = '';
    }
}

function sendQuickAgentCommand(cmd) {
    switchTab('agent');
    sendAgentMessage(cmd);
}

function triggerNewHireDemo() {
    switchTab('agent');
    sendAgentMessage("Onboard Kavita Sharma as Senior Cloud Architect in Engineering and configure company mail");
}

function triggerPatrolDemo() {
    switchTab('agent');
    sendAgentMessage("Run an autonomous patrol across all departments and report critical flight risks");
}

// Hook message input enter key
document.addEventListener('DOMContentLoaded', () => {
    const msgInput = document.getElementById('agent-message-input');
    if (msgInput) {
        msgInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') submitAgentChat();
        });
    }
    renderChatStream();
});

// Autonomous IT Provisioning & Onboarding Handlers
function fillPresetOnboard(name, role, dept, email) {
    const nameEl = document.getElementById('onboard-name-input');
    const roleEl = document.getElementById('onboard-role-input');
    const deptEl = document.getElementById('onboard-dept-select');
    const emailEl = document.getElementById('onboard-email-input');

    if (nameEl) nameEl.value = name;
    if (roleEl) roleEl.value = role;
    if (deptEl) deptEl.value = dept;
    if (emailEl) emailEl.value = email;
}

async function submitAutonomousOnboarding() {
    const name = document.getElementById('onboard-name-input')?.value?.trim();
    const role = document.getElementById('onboard-role-input')?.value?.trim();
    const dept = document.getElementById('onboard-dept-select')?.value;
    const email = document.getElementById('onboard-email-input')?.value?.trim();
    const btn = document.getElementById('btn-submit-onboarding');

    if (!name || !role) {
        alert('Please specify candidate full name and role title.');
        return;
    }

    const originalText = btn.innerHTML;
    btn.innerHTML = '<span>⚡ Provisioning Cloud & Mail...</span>';
    btn.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/agent/onboard-new-hire`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                candidate_name: name,
                role_title: role,
                department: dept,
                personal_email: email
            })
        });
        const data = await res.json();

        // Populate Receipt Panel
        const titleEl = document.getElementById('receipt-hire-title');
        const timeEl = document.getElementById('receipt-timestamp');
        const mailEl = document.getElementById('receipt-email');
        const ssoEl = document.getElementById('receipt-sso');
        const passEl = document.getElementById('receipt-password');
        const lapEl = document.getElementById('receipt-laptop');
        const courierEl = document.getElementById('receipt-courier');
        const buddyEl = document.getElementById('receipt-buddy');
        const panel = document.getElementById('onboarding-receipt-panel');

        if (titleEl) titleEl.textContent = `Identity & Systems Provisioned for ${data.employee_name}`;
        if (timeEl) timeEl.textContent = data.dispatch_timestamp || new Date().toLocaleTimeString();
        if (mailEl) mailEl.textContent = data.corporate_email;
        if (ssoEl) ssoEl.textContent = data.sso_username;
        if (passEl) passEl.textContent = data.temporary_password;
        if (lapEl) lapEl.textContent = data.hardware_and_stipend?.primary_laptop || 'Apple MacBook Pro 16" M3 Max';
        if (courierEl) courierEl.textContent = data.hardware_and_stipend?.dispatch_status || 'Courier Dispatched (#WS-88392-US)';
        if (buddyEl) buddyEl.textContent = data.assigned_buddy;

        if (panel) {
            panel.classList.remove('hidden');
            panel.scrollIntoView({ behavior: 'smooth' });
        }

        loadAgentStatus();
        loadAgentFeed();
        loadHRActions();
        loadAuditTrail();
    } catch (err) {
        console.error('Failed to provision new hire:', err);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function loadExecutiveBriefing() {
    try {
        const res = await fetch(`${API_BASE}/agent/briefing`);
        const data = await res.json();
        const el = document.getElementById('briefing-headline');
        if (el && data.headline) {
            el.textContent = `${data.headline} Operating under ${data.operating_mode}. Total financial savings secured: $${Number(data.financial_savings_secured_usd).toLocaleString()}.`;
        }
    } catch (err) {
        console.error('Failed to load executive briefing:', err);
    }
}
