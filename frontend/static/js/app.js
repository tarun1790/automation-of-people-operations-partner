// WorkSight AI - Client Application Logic

const API_BASE = '/api/v1';

// App State
let currentTab = 'dashboard';
let currentDepartment = 'Engineering';
let anonymizeBias = false;

// Initialize on DOM ready
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
});

// Navigation Handling
function initNavigation() {
    const navButtons = document.querySelectorAll('[data-tab]');
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

    document.querySelectorAll('[data-tab]').forEach(btn => {
        if (btn.getAttribute('data-tab') === tabId) {
            btn.classList.add('bg-indigo-600', 'text-white');
            btn.classList.remove('text-gray-300', 'hover:bg-gray-800');
        } else {
            btn.classList.remove('bg-indigo-600', 'text-white');
            btn.classList.add('text-gray-300', 'hover:bg-gray-800');
        }
    });

    if (tabId === 'skills') {
        renderSkillGraphCanvas();
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

// 2. Risk Radar
async function loadRiskRadar() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/risk-radar`);
        const data = await res.json();
        const container = document.getElementById('risk-radar-cards');
        if (!container) return;

        container.innerHTML = '';
        data.department_risk_matrix.forEach(dept => {
            const badgeClass = dept.risk_level === 'CRITICAL' ? 'badge-critical' :
                               dept.risk_level === 'HIGH' ? 'badge-high' :
                               dept.risk_level === 'MODERATE' ? 'badge-moderate' : 'badge-low';

            const card = document.createElement('div');
            card.className = 'glass-card p-4 flex flex-col justify-between';
            card.innerHTML = `
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-bold text-base text-gray-100">${dept.department}</span>
                        <span class="px-2 py-0.5 text-xs font-semibold rounded ${badgeClass}">${dept.risk_level}</span>
                    </div>
                    <div class="text-xs text-gray-400 mb-2">Headcount: <strong class="text-gray-200">${dept.headcount}</strong> | Risk Score: <strong class="text-gray-200">${dept.risk_score}/100</strong></div>
                    <div class="space-y-1 mb-3">
                        ${dept.detected_signals.map(s => `<div class="text-xs text-gray-300 flex items-start"><span class="text-amber-400 mr-1.5">•</span><span>${s}</span></div>`).join('')}
                    </div>
                </div>
                <div class="pt-2 border-t border-gray-800 text-xs text-indigo-300 flex justify-between items-center">
                    <span>Avg Overtime: ${dept.metrics.avg_overtime_hrs}h/mo</span>
                    <button onclick="openSimulationForDept('${dept.department}')" class="text-xs text-indigo-400 hover:text-indigo-200 underline">Simulate Impact →</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error('Failed to load risk radar:', err);
    }
}

// 3. AI Insight Cards
async function loadAIInsights() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/insights`);
        const insights = await res.json();
        const container = document.getElementById('ai-insights-container');
        if (!container) return;

        container.innerHTML = '';
        insights.forEach(ins => {
            const card = document.createElement('div');
            card.className = 'glass-card p-5 border-l-4 border-indigo-500 flex flex-col justify-between';
            card.innerHTML = `
                <div>
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-xs uppercase font-bold tracking-wider text-indigo-400">${ins.badge}</span>
                        <span class="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded font-mono">Confidence: ${ins.confidence}%</span>
                    </div>
                    <h4 class="text-sm font-semibold text-white mb-2">${ins.target}</h4>
                    <p class="text-xs text-gray-300 mb-3">${ins.finding}</p>
                    <div class="bg-gray-900/60 p-2.5 rounded mb-3 space-y-1">
                        <div class="text-xs font-semibold text-gray-400 mb-1">Key Correlated Evidence:</div>
                        ${ins.evidence.map(e => `<div class="text-xs text-gray-300 flex items-start"><span class="text-indigo-400 mr-1.5">•</span><span>${e}</span></div>`).join('')}
                    </div>
                    <div class="text-xs text-amber-200/90 mb-3"><strong>Recommended Action:</strong> ${ins.recommended_action}</div>
                </div>
                <div class="flex gap-2 pt-2 border-t border-gray-800">
                    <button onclick="switchTab('actions')" class="flex-1 py-1.5 px-3 bg-indigo-600 hover:bg-indigo-700 text-xs font-medium rounded text-white transition">Review in Action Center</button>
                    <button onclick="switchTab('simulation')" class="py-1.5 px-3 bg-gray-800 hover:bg-gray-700 text-xs font-medium rounded text-gray-200 transition">Simulate</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error('Failed to load AI insights:', err);
    }
}

// 4. Natural Language AI Command Center
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
    outputArea.innerHTML = `
        <div class="flex items-center gap-2 text-indigo-400 text-sm py-4">
            <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
            <span>Cross-Source Reasoning Engine evaluating workforce evidence...</span>
        </div>
    `;

    try {
        const res = await fetch(`${API_BASE}/dashboard/command-center`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        const data = await res.json();

        outputArea.innerHTML = `
            <div class="glass-card p-5 border border-indigo-500/40 mt-3 space-y-3">
                <div class="flex justify-between items-center text-xs pb-2 border-b border-gray-800">
                    <span class="text-indigo-400 font-mono">Tool Executed: <strong>${data.tool_called}</strong></span>
                    <span class="bg-indigo-950 text-indigo-300 px-2 py-0.5 rounded font-mono">Confidence: ${data.confidence}%</span>
                </div>
                <div>
                    <h4 class="text-sm font-semibold text-white mb-1">Executive Finding & Synthesis:</h4>
                    <p class="text-xs text-gray-200 leading-relaxed">${data.executive_summary}</p>
                </div>
                <div class="bg-gray-900/70 p-3 rounded text-xs space-y-1.5">
                    <div class="font-semibold text-gray-400">Underlying Correlated Evidence:</div>
                    <pre class="font-mono text-xs text-gray-300 whitespace-pre-wrap overflow-x-auto">${JSON.stringify(data.evidence, null, 2)}</pre>
                </div>
                <div class="bg-indigo-900/20 p-3 rounded border border-indigo-800/40 text-xs">
                    <span class="font-semibold text-amber-300">Recommended Action:</span>
                    <p class="text-gray-200 mt-0.5">${data.recommended_action}</p>
                    <div class="text-emerald-400 mt-1"><strong>Expected Impact:</strong> ${data.expected_impact}</div>
                </div>
            </div>
        `;
    } catch (err) {
        outputArea.innerHTML = `<div class="text-rose-400 text-xs py-2">Error processing command: ${err.message}</div>`;
    }
}

// 5. What-If Scenario Simulator
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

    // Initial run
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
    impEl.className = imp >= 0 ? 'text-xl font-bold text-emerald-400' : 'text-xl font-bold text-rose-400';

    document.getElementById('sim-prevented-departures').textContent = data.impact_analysis.departures_prevented_annually;
    document.getElementById('sim-turnover-savings').textContent = `$${data.impact_analysis.turnover_replacement_savings_usd.toLocaleString()}`;
    document.getElementById('sim-net-roi').textContent = `$${data.impact_analysis.net_annual_financial_benefit_usd.toLocaleString()}`;
    document.getElementById('sim-disclaimer').textContent = data.model_disclaimer;
}

// 6. HR Action Center & Human-in-the-Loop Review
async function loadHRActions() {
    try {
        const res = await fetch(`${API_BASE}/governance/actions`);
        const actions = await res.json();
        const container = document.getElementById('actions-table-body');
        if (!container) return;

        container.innerHTML = '';
        actions.forEach(act => {
            const row = document.createElement('tr');
            row.className = 'border-b border-gray-800 hover:bg-gray-800/40 text-xs transition';

            const statusClass = act.status === 'Approved' ? 'text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded' :
                                act.status === 'Executed' ? 'text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded' :
                                act.status === 'Rejected' ? 'text-rose-400 bg-rose-950/40 px-2 py-0.5 rounded' :
                                'text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded';

            row.innerHTML = `
                <td class="p-3 font-mono text-gray-400">#ACT-${act.action_id}</td>
                <td class="p-3 font-semibold text-gray-100">${act.title}</td>
                <td class="p-3 text-gray-300">${act.target_entity}</td>
                <td class="p-3"><span class="px-1.5 py-0.5 text-xs font-semibold rounded ${act.priority === 'Critical' ? 'badge-critical' : 'badge-high'}">${act.priority}</span></td>
                <td class="p-3 text-gray-300 max-w-xs truncate">${act.expected_impact}</td>
                <td class="p-3"><span class="${statusClass}">${act.status}</span></td>
                <td class="p-3">
                    ${act.status === 'Pending Approval' ? `
                        <div class="flex gap-1">
                            <button onclick="reviewAction(${act.action_id}, 'Approved')" class="px-2 py-1 bg-emerald-700 hover:bg-emerald-600 text-white rounded font-medium">Approve</button>
                            <button onclick="reviewAction(${act.action_id}, 'Rejected')" class="px-2 py-1 bg-rose-800 hover:bg-rose-700 text-white rounded">Dismiss</button>
                        </div>
                    ` : act.status === 'Approved' ? `
                        <button onclick="reviewAction(${act.action_id}, 'Executed')" class="px-2 py-1 bg-cyan-700 hover:bg-cyan-600 text-white rounded font-medium">Execute</button>
                    ` : `<span class="text-gray-500 italic">Logged</span>`}
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
                notes: `Action marked as ${decision} via Executive Dashboard.`
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
            row.className = 'border-b border-gray-800 hover:bg-gray-800/30 text-xs font-mono';
            row.innerHTML = `
                <td class="p-2.5 text-gray-400">${l.timestamp}</td>
                <td class="p-2.5 text-indigo-400 font-semibold">${l.event_type}</td>
                <td class="p-2.5 text-gray-300">${l.actor}</td>
                <td class="p-2.5 text-gray-200 max-w-sm truncate">${l.summary}</td>
                <td class="p-2.5 text-gray-500">${l.model_version}</td>
            `;
            container.appendChild(row);
        });
    } catch (err) {
        console.error('Failed to load audit trail:', err);
    }
}

// 8. Workforce Risk & Attrition Predictions
async function loadAttritionPredictions() {
    try {
        const res = await fetch(`${API_BASE}/workforce/attrition-predictions`);
        const preds = await res.json();
        const container = document.getElementById('attrition-table-body');
        if (!container) return;

        container.innerHTML = '';
        preds.forEach(p => {
            const row = document.createElement('tr');
            row.className = 'border-b border-gray-800 hover:bg-gray-800/40 text-xs transition';

            const badgeClass = p.risk_level === 'CRITICAL' ? 'badge-critical' :
                               p.risk_level === 'HIGH' ? 'badge-high' :
                               p.risk_level === 'MODERATE' ? 'badge-moderate' : 'badge-low';

            row.innerHTML = `
                <td class="p-3 font-mono text-gray-400">${p.employee_code}</td>
                <td class="p-3 font-semibold text-gray-100">${p.employee_name}</td>
                <td class="p-3 text-gray-300">${p.department}</td>
                <td class="p-3 text-gray-300">${p.role_title}</td>
                <td class="p-3 font-mono font-bold text-gray-100">${(p.attrition_probability * 100).toFixed(1)}%</td>
                <td class="p-3"><span class="px-2 py-0.5 font-semibold rounded ${badgeClass}">${p.risk_level}</span></td>
                <td class="p-3 max-w-xs text-gray-300">
                    <div class="space-y-0.5">
                        ${p.top_contributing_factors.slice(0, 2).map(f => `<div><span class="text-rose-400 font-mono">${f.impact_pct}</span> ${f.factor}</div>`).join('')}
                    </div>
                </td>
                <td class="p-3 text-gray-300 text-xs italic max-w-xs">${p.defensible_statement}</td>
            `;
            container.appendChild(row);
        });
    } catch (err) {
        console.error('Failed to load attrition predictions:', err);
    }
}

// 9. Talent Intelligence & Candidate Ranking
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
            opt.textContent = `${p.req_code} - ${p.title} (${p.candidate_count} candidates)`;
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
            const badgeClass = c.recommendation === 'Strong Hire' ? 'badge-low' :
                               c.recommendation === 'Consider' ? 'badge-high' : 'badge-critical';

            const card = document.createElement('div');
            card.className = 'glass-card p-4 flex flex-col justify-between';
            card.innerHTML = `
                <div>
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-xs font-mono text-indigo-400 font-bold">Rank #${idx + 1}</span>
                        <span class="px-2 py-0.5 text-xs font-semibold rounded ${badgeClass}">${c.recommendation}</span>
                    </div>
                    <h4 class="text-sm font-semibold text-white mb-1">${c.full_name}</h4>
                    <div class="text-xs text-gray-400 mb-2">${c.current_title || 'Candidate'} | Exp: ${c.years_of_experience} yrs</div>
                    
                    <div class="grid grid-cols-2 gap-2 bg-gray-900/60 p-2.5 rounded text-xs mb-3">
                        <div>Skill Match: <strong class="text-indigo-300 font-mono">${c.skill_match_pct}%</strong></div>
                        <div>Exp Align: <strong class="text-indigo-300 font-mono">${c.experience_alignment_pct}%</strong></div>
                        <div class="col-span-2 pt-1 border-t border-gray-800">Composite Score: <strong class="text-emerald-400 font-mono text-sm">${c.composite_score}%</strong></div>
                    </div>

                    <div class="text-xs mb-2">
                        <span class="text-gray-400 font-semibold">Strengths:</span>
                        <div class="text-gray-300 flex flex-wrap gap-1 mt-1">
                            ${c.key_strengths.map(s => `<span class="bg-gray-800 text-gray-300 px-1.5 py-0.5 rounded text-[11px]">${s}</span>`).join('')}
                        </div>
                    </div>

                    ${c.skill_gaps.length > 0 ? `
                        <div class="text-xs mb-3">
                            <span class="text-rose-400 font-semibold">Skill Gaps:</span>
                            <div class="text-gray-300 flex flex-wrap gap-1 mt-1">
                                ${c.skill_gaps.map(g => `<span class="bg-rose-950/40 text-rose-300 px-1.5 py-0.5 rounded text-[11px]">${g}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
                <div class="pt-2 border-t border-gray-800 text-xs text-gray-400 flex justify-between">
                    <span>Stage: <strong>${c.stage}</strong></span>
                    <button onclick="prefillInterviewCandidate('${c.full_name}')" class="text-indigo-400 hover:text-indigo-300 underline">Start Interview →</button>
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
                opt.textContent = `Q${idx + 1} (${q.category}): ${q.question.substring(0, 75)}...`;
                questionsSelect.appendChild(opt);
            });
            criteriaBox.textContent = loadedQuestions[0].criteria;
        } catch (err) {
            console.error('Error generating interview questions:', err);
        } finally {
            genBtn.disabled = false;
            genBtn.textContent = 'Generate Questions';
        }
    });

    questionsSelect.addEventListener('change', () => {
        const q = loadedQuestions[questionsSelect.value];
        if (q) criteriaBox.textContent = q.criteria;
    });

    // Sample Answer Fill buttons
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
        evalBtn.textContent = 'Analyzing Response...';

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
                <div class="glass-card p-5 border border-indigo-500/40 space-y-3">
                    <div class="flex justify-between items-center pb-2 border-b border-gray-800">
                        <span class="text-xs font-semibold uppercase text-indigo-400 tracking-wider">Evaluation Scorecard</span>
                        <span class="px-2.5 py-1 text-xs font-bold rounded ${evalData.signal === 'Strong Hire' ? 'bg-emerald-950 text-emerald-300 border border-emerald-700' : 'bg-rose-950 text-rose-300 border border-rose-700'}">${evalData.signal}</span>
                    </div>

                    <div class="grid grid-cols-4 gap-2 text-center bg-gray-900/60 p-3 rounded">
                        <div>
                            <div class="text-[11px] text-gray-400">Technical Depth</div>
                            <div class="text-base font-bold text-white font-mono">${evalData.technical_correctness_score}%</div>
                        </div>
                        <div>
                            <div class="text-[11px] text-gray-400">STAR Structure</div>
                            <div class="text-base font-bold text-white font-mono">${evalData.star_structure_score}%</div>
                        </div>
                        <div>
                            <div class="text-[11px] text-gray-400">Relevance</div>
                            <div class="text-base font-bold text-white font-mono">${evalData.relevance_score}%</div>
                        </div>
                        <div>
                            <div class="text-[11px] text-gray-400">Overall Score</div>
                            <div class="text-base font-bold text-emerald-400 font-mono">${evalData.overall_score}%</div>
                        </div>
                    </div>

                    <div class="text-xs text-gray-200">
                        <span class="font-semibold text-emerald-400">Strengths:</span>
                        <ul class="list-disc list-inside mt-1 text-gray-300">
                            ${evalData.strengths.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="text-xs text-gray-200">
                        <span class="font-semibold text-rose-400">Missing Elements:</span>
                        <ul class="list-disc list-inside mt-1 text-gray-300">
                            ${evalData.missing_aspects.map(m => `<li>${m}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="bg-indigo-950/40 p-2.5 rounded border border-indigo-800/40 text-xs">
                        <span class="font-semibold text-amber-300">Suggested Follow-Up Probing Question:</span>
                        <p class="text-gray-200 italic mt-0.5">"${evalData.suggested_follow_up}"</p>
                    </div>
                </div>
            `;
        } catch (err) {
            scorecardArea.innerHTML = `<div class="text-rose-400 text-xs">Evaluation error: ${err.message}</div>`;
        } finally {
            evalBtn.disabled = false;
            evalBtn.textContent = 'Evaluate Candidate Answer';
        }
    });
}

function prefillInterviewCandidate(name) {
    switchTab('talent');
    const answerInput = document.getElementById('interview-answer-input');
    if (answerInput) {
        answerInput.scrollIntoView({ behavior: 'smooth' });
    }
}

// 11. Performance Intelligence & 9-Box Matrix
async function loadPerformanceMatrix() {
    try {
        const res = await fetch(`${API_BASE}/workforce/performance-matrix`);
        const data = await res.json();

        document.getElementById('perf-avg-score').textContent = `${data.average_performance} / 5.0`;
        document.getElementById('perf-hipo-count').textContent = data.high_potential_count;
        document.getElementById('perf-coaching-count').textContent = data.growth_coaching_needed_count;

        const cells = document.querySelectorAll('.nine-box-cell');
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
        row.className = 'border-b border-gray-800 hover:bg-gray-800/40 text-xs transition';
        row.innerHTML = `
            <td class="p-3 font-semibold text-gray-100">${item.employee_name}</td>
            <td class="p-3 text-gray-300">${item.department}</td>
            <td class="p-3 text-gray-300">${item.role_title}</td>
            <td class="p-3 font-mono font-bold text-gray-100">${item.performance_score}</td>
            <td class="p-3"><span class="px-2 py-0.5 bg-gray-800 rounded text-xs">${item.quadrant_name}</span></td>
            <td class="p-3 font-mono text-emerald-400 font-bold">${item.promotion_readiness_score}%</td>
            <td class="p-3 text-gray-300 max-w-xs truncate">${item.recommended_path}</td>
        `;
        container.appendChild(row);
    });
}

function filterPerformanceTable(allItems, quadrantName) {
    const filtered = allItems.filter(i => i.quadrant_name === quadrantName);
    renderPerformanceTable(filtered);
}

// 12. Workforce Skill Graph Canvas Visualization & Mobility Pathfinder
let skillGraphData = null;

async function loadSkillGraph() {
    try {
        const res = await fetch(`${API_BASE}/workforce/skills-graph`);
        skillGraphData = await res.json();

        // Render SPOF alerts
        const spofContainer = document.getElementById('spof-alerts-container');
        if (spofContainer) {
            spofContainer.innerHTML = '';
            skillGraphData.critical_single_points_of_failure.forEach(s => {
                const alertCard = document.createElement('div');
                alertCard.className = 'glass-card p-3 border-l-4 border-rose-500 text-xs space-y-1';
                alertCard.innerHTML = `
                    <div class="flex justify-between items-center">
                        <strong class="text-rose-400 font-semibold">${s.vulnerability_level}</strong>
                        <span class="bg-rose-950/60 text-rose-300 px-1.5 py-0.5 rounded font-mono">1 Expert Holder</span>
                    </div>
                    <div class="text-sm font-bold text-white">${s.skill_name}</div>
                    <div class="text-gray-300">Solely held by <strong class="text-indigo-300">${s.holder_name}</strong> (${s.holder_department} - ${s.holder_role}).</div>
                    <div class="text-amber-200 mt-1"><strong>Action:</strong> ${s.mitigation_plan}</div>
                `;
                spofContainer.appendChild(alertCard);
            });
        }

        // Render Department Coverage
        const deptCovContainer = document.getElementById('dept-coverage-bars');
        if (deptCovContainer) {
            deptCovContainer.innerHTML = '';
            Object.entries(skillGraphData.department_skill_coverage).forEach(([dept, cov]) => {
                const bar = document.createElement('div');
                bar.className = 'text-xs space-y-1';
                bar.innerHTML = `
                    <div class="flex justify-between text-gray-300">
                        <span>${dept}</span>
                        <span class="font-mono font-bold">${cov}%</span>
                    </div>
                    <div class="w-full bg-gray-800 h-2 rounded overflow-hidden">
                        <div class="bg-indigo-500 h-full rounded" style="width: ${cov}%;"></div>
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
    canvas.height = 480;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Filter nodes for canvas visualization
    const skillNodes = skillGraphData.nodes.filter(n => n.type === 'skill').slice(0, 14);
    const empNodes = skillGraphData.nodes.filter(n => n.type === 'employee').slice(0, 10);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) * 0.38;

    // Position Skills on outer circle
    skillNodes.forEach((s, i) => {
        const angle = (i / skillNodes.length) * 2 * Math.PI;
        s.x = centerX + radius * Math.cos(angle);
        s.y = centerY + radius * Math.sin(angle);
    });

    // Position Employees on inner circle
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
            ctx.strokeStyle = 'rgba(99, 102, 241, 0.25)';
            ctx.beginPath();
            ctx.moveTo(sourceNode.x, sourceNode.y);
            ctx.lineTo(targetNode.x, targetNode.y);
            ctx.stroke();
        }
    });

    // Draw Skill Nodes
    skillNodes.forEach(s => {
        const isSPOF = skillGraphData.critical_single_points_of_failure.some(sp => sp.skill_name === s.label);
        ctx.fillStyle = isSPOF ? '#f43f5e' : '#3b82f6';
        ctx.beginPath();
        ctx.arc(s.x, s.y, isSPOF ? 8 : 6, 0, 2 * Math.PI);
        ctx.fill();

        ctx.fillStyle = '#9ca3af';
        ctx.font = '10px Inter, sans-serif';
        ctx.textAlign = s.x > centerX ? 'left' : 'right';
        ctx.fillText(s.label, s.x > centerX ? s.x + 10 : s.x - 10, s.y + 3);
    });

    // Draw Employee Nodes
    empNodes.forEach(e => {
        ctx.fillStyle = '#10b981';
        ctx.beginPath();
        ctx.arc(e.x, e.y, 7, 0, 2 * Math.PI);
        ctx.fill();

        ctx.fillStyle = '#f3f4f6';
        ctx.font = '11px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(e.label.split(' ')[0], e.x, e.y - 10);
    });
}

function setupMobilityPathfinder() {
    const btn = document.getElementById('calc-mobility-btn');
    const roleSelect = document.getElementById('mobility-target-role');
    const resultArea = document.getElementById('mobility-result-area');
    if (!btn) return;

    btn.addEventListener('click', async () => {
        btn.disabled = true;
        btn.textContent = 'Computing Path...';

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
                <div class="glass-card p-4 border border-indigo-500/40 space-y-3">
                    <div class="flex justify-between items-center text-xs pb-2 border-b border-gray-800">
                        <span class="text-gray-300">Target Role: <strong class="text-white">${data.target_role}</strong></span>
                        <span class="text-emerald-400 font-mono font-bold">Readiness: ${data.readiness_pct}%</span>
                    </div>
                    <div class="text-xs">
                        <div class="font-semibold text-emerald-400 mb-1">Matched Competencies:</div>
                        <div class="flex flex-wrap gap-1">
                            ${data.matched_competencies.map(m => `<span class="bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded text-[11px]">${m.skill} (${m.current_proficiency})</span>`).join('')}
                        </div>
                    </div>
                    <div class="text-xs">
                        <div class="font-semibold text-rose-400 mb-1">Skill Gaps & Recommended Upskilling:</div>
                        <div class="space-y-1 text-gray-300">
                            ${data.missing_competencies.map(m => `<div class="flex items-center gap-1.5"><span class="text-rose-400">•</span><span><strong>${m.skill}:</strong> ${m.recommended_course}</span></div>`).join('')}
                        </div>
                    </div>
                    <div class="text-xs text-indigo-300 pt-1 border-t border-gray-800">
                        Estimated Transition Timeline: <strong>${data.estimated_readiness_timeline}</strong>
                    </div>
                </div>
            `;
        } catch (err) {
            console.error('Mobility error:', err);
        } finally {
            btn.disabled = false;
            btn.textContent = 'Calculate Upskilling Path';
        }
    });
}

// 13. Adaptive Onboarding
async function loadOnboardingJourneys() {
    try {
        const res = await fetch(`${API_BASE}/workforce/onboarding-journeys`);
        const journeys = await res.json();
        const container = document.getElementById('onboarding-cards-container');
        if (!container) return;

        container.innerHTML = '';
        journeys.forEach(j => {
            const card = document.createElement('div');
            card.className = 'glass-card p-5 space-y-4';
            card.innerHTML = `
                <div class="flex justify-between items-start pb-3 border-b border-gray-800">
                    <div>
                        <div class="text-xs text-gray-400 uppercase font-mono">${j.cohort} • Day ${j.current_day} of 90</div>
                        <h4 class="text-base font-bold text-white">${j.employee_name}</h4>
                        <div class="text-xs text-indigo-300">${j.role_title} (${j.department})</div>
                    </div>
                    <div class="text-right">
                        <span class="px-2 py-0.5 text-xs font-semibold rounded ${j.status === 'Ahead' ? 'badge-low' : j.status === 'AtRisk' ? 'badge-critical' : 'badge-moderate'}">${j.status}</span>
                        <div class="text-xs text-gray-400 mt-1">Buddy: <strong class="text-gray-200">${j.assigned_buddy}</strong></div>
                    </div>
                </div>

                <div>
                    <div class="flex justify-between text-xs text-gray-300 mb-1">
                        <span>Milestone Progress</span>
                        <span class="font-mono font-bold text-indigo-400">${j.progress_pct}%</span>
                    </div>
                    <div class="w-full bg-gray-800 h-2.5 rounded overflow-hidden">
                        <div class="bg-indigo-600 h-full rounded" style="width: ${j.progress_pct}%;"></div>
                    </div>
                </div>

                <div class="text-xs text-gray-300 bg-gray-900/60 p-2.5 rounded">
                    <strong>Adaptive Guidance:</strong> ${j.adaptive_notes || 'Milestones progressing on schedule.'}
                </div>

                <div class="space-y-2">
                    <div class="text-xs font-semibold text-gray-400">Milestone Action Checklist:</div>
                    ${j.tasks.map(t => `
                        <div class="flex items-start gap-2 text-xs text-gray-200 p-2 bg-gray-900/40 rounded hover:bg-gray-800/60 transition">
                            <input type="checkbox" ${t.is_completed ? 'checked' : ''} onchange="toggleTask(${t.id}, this.checked)" class="mt-0.5 rounded border-gray-700 text-indigo-600">
                            <div class="flex-1">
                                <div class="${t.is_completed ? 'line-through text-gray-500' : 'font-medium'}">${t.task_name}</div>
                                <div class="text-[11px] text-gray-400">${t.milestone_phase} • ${t.category}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error('Failed to load onboarding journeys:', err);
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

// 14. Policy Intelligence (Source-Grounded RAG)
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
                <div class="glass-card p-5 border border-indigo-500/40 space-y-3">
                    <div class="flex justify-between items-center pb-2 border-b border-gray-800 text-xs">
                        <span class="text-indigo-400 font-semibold uppercase">Source-Grounded Response</span>
                        <span class="bg-indigo-950 text-indigo-300 px-2 py-0.5 rounded font-mono">Confidence: ${data.confidence}%</span>
                    </div>

                    <div class="text-sm text-gray-100 leading-relaxed">${data.answer.replace(/\n/g, '<br/>')}</div>

                    ${data.citations && data.citations.length > 0 ? `
                        <div class="bg-gray-900/80 p-3 rounded border border-gray-800 text-xs space-y-2">
                            <div class="font-semibold text-gray-400">Exact Handbook Citations & Page References:</div>
                            ${data.citations.map(c => `
                                <div class="p-2 bg-gray-950/60 rounded border border-gray-800">
                                    <div class="flex justify-between text-indigo-300 font-mono text-[11px] mb-1">
                                        <span>${c.document_title} (${c.policy_code})</span>
                                        <span>Page ${c.page_number} • ${c.section_title}</span>
                                    </div>
                                    <div class="text-gray-300 italic">"${c.retrieved_excerpt}"</div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}

                    <div class="text-xs text-amber-300/90 pt-1">
                        <strong>Recommended Procedure:</strong> ${data.recommended_action || 'Consult HR Partner'}
                    </div>
                    <div class="text-[11px] text-gray-500 italic">
                        ${data.governance_notice}
                    </div>
                </div>
            `;
        } catch (err) {
            resultArea.innerHTML = `<div class="text-rose-400 text-xs">Policy search error: ${err.message}</div>`;
        } finally {
            btn.disabled = false;
            btn.textContent = 'Query Policy';
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

// 15. Governance, MLOps, Data Quality & Fairness
async function loadGovernanceTelemetry() {
    try {
        // MLOps Telemetry
        const mlRes = await fetch(`${API_BASE}/governance/mlops-telemetry`);
        const mlData = await mlRes.json();
        document.getElementById('mlops-accuracy').textContent = `${(mlData.accuracy * 100).toFixed(1)}%`;
        document.getElementById('mlops-precision').textContent = `${(mlData.precision * 100).toFixed(1)}%`;
        document.getElementById('mlops-recall').textContent = `${(mlData.recall * 100).toFixed(1)}%`;
        document.getElementById('mlops-f1').textContent = `${(mlData.f1_score * 100).toFixed(1)}%`;
        document.getElementById('mlops-roc-auc').textContent = mlData.roc_auc.toFixed(3);
        document.getElementById('mlops-latency').textContent = `${mlData.avg_latency_ms} ms`;
        document.getElementById('mlops-device').textContent = mlData.device;

        // Data Quality
        const dqRes = await fetch(`${API_BASE}/governance/data-quality`);
        const dqData = await dqRes.json();
        document.getElementById('dq-score').textContent = `${dqData.data_quality_score}%`;
        document.getElementById('dq-status').textContent = dqData.validation_status;
        document.getElementById('dq-missing').textContent = `${dqData.missing_values_pct}%`;
        document.getElementById('dq-duplicates').textContent = `${dqData.duplicates_pct}%`;
        document.getElementById('dq-invalid').textContent = `${dqData.invalid_records_pct}%`;
        document.getElementById('dq-last-check').textContent = dqData.last_validated;

        // Fairness Monitor
        const fairRes = await fetch(`${API_BASE}/governance/fairness-monitor`);
        const fairData = await fairRes.json();
        document.getElementById('fair-parity-score').textContent = `${fairData.demographic_parity_score}/100`;
        document.getElementById('fair-adverse-ratio').textContent = fairData.adverse_impact_ratio;
        document.getElementById('fair-status').textContent = fairData.four_fifths_rule_status;
    } catch (err) {
        console.error('Failed to load governance telemetry:', err);
    }
}
