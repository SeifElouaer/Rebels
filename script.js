// Configuration
const API_BASE_URL = 'http://localhost:5000';

// State
let currentView = 'dashboard';

// DOM Elements
const views = document.querySelectorAll('.view');
const navLinks = document.querySelectorAll('.nav-links li');
const systemStatus = document.getElementById('systemStatus');
const evaluationForm = document.getElementById('evaluationForm');
const resultPanel = document.getElementById('resultPanel');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    checkBackendHealth();
    loadStats();

    // Auto-refresh stats every 60 seconds
    setInterval(loadStats, 60000);
});

// Navigation Logic
function initNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const targetView = link.getAttribute('data-view');
            switchView(targetView);

            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

function switchView(viewId) {
    views.forEach(view => {
        view.classList.remove('active');
        if (view.id === `${viewId}View`) {
            view.classList.add('active');
        }
    });
    currentView = viewId;
}

// API Interactions
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            systemStatus.classList.add('online');
            systemStatus.querySelector('.status-text').textContent = 'System Online';
        } else {
            systemStatus.classList.remove('online');
            systemStatus.querySelector('.status-text').textContent = 'Backend Issue';
        }

        // Update LLM Status
        const llmText = document.getElementById('llmStatusText');
        const llmBadge = document.getElementById('llmStatus');
        if (data.llm === 'configured') {
            llmText.textContent = 'Active';
            llmBadge.style.opacity = '1';
            llmBadge.title = 'Gemini 1.5 Flash is generating personalized explanations';
        } else {
            llmText.textContent = 'Template Only';
            llmBadge.style.opacity = '0.7';
            llmBadge.title = 'LLM not configured. Falling back to template explanations.';
        }
    } catch (error) {
        systemStatus.classList.remove('online');
        systemStatus.querySelector('.status-text').textContent = 'Offline';
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        const data = await response.json();

        // Update Stats Cards
        document.getElementById('statTotalClients').textContent = data.total_clients.toLocaleString();
        document.getElementById('statTotalApps').textContent = data.total_applications.toLocaleString();

        // Calculate Success Rate from distribution
        const success = data.outcome_distribution.success || 0;
        const total = data.total_applications || 1;
        const rate = (success / total) * 100;
        document.getElementById('statSuccessRate').textContent = `${rate.toFixed(1)}%`;

        // Populate Distribution List
        const list = document.getElementById('outcomeList');
        list.innerHTML = '';

        Object.entries(data.outcome_distribution).forEach(([outcome, count]) => {
            const item = document.createElement('div');
            item.className = 'outcome-item';
            item.innerHTML = `
                <span class="outcome-label">${outcome.replace('_', ' ')}</span>
                <span class="outcome-count">${count.toLocaleString()}</span>
                <div class="outcome-progress"><div class="fill" style="width: ${(count / total) * 100}%"></div></div>
            `;
            list.appendChild(item);
        });

    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Evaluation Logic
evaluationForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // UI Feedback
    const submitBtn = evaluationForm.querySelector('button');
    const originalBtnContent = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

    // Gather Data
    const formData = new FormData(evaluationForm);
    const payload = Object.fromEntries(formData.entries());

    // Convert numbers
    payload.requested_amount = parseFloat(payload.requested_amount);
    payload.annual_income_snapshot = parseFloat(payload.annual_income_snapshot);
    payload.fico_snapshot = parseFloat(payload.fico_snapshot);
    payload.monthly_debt = parseFloat(payload.monthly_debt);

    // Auto-calculate DTI Ratio (%)
    const monthlyIncome = payload.annual_income_snapshot / 12;
    payload.dti_snapshot = (payload.monthly_debt / monthlyIncome) * 100;

    // Add default values for required embedding fields not in form
    payload.payment_to_income_ratio = (payload.requested_amount / 36) / (payload.annual_income_snapshot / 12);
    payload.loan_to_income_ratio = payload.requested_amount / payload.annual_income_snapshot;
    payload.nb_previous_loans = 0;
    payload.open_accounts = 5;
    payload.total_accounts = 10;
    payload.delinquencies_2y = 0;
    payload.inquiries_6m = 0;
    payload.public_records = 0;
    payload.credit_history_length_snapshot = 5.0;
    payload.revolving_utilization_snapshot = 30.0;

    try {
        const response = await fetch(`${API_BASE_URL}/api/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        displayResult(result, payload);

    } catch (error) {
        alert('Error communicating with the evaluation engine.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnContent;
    }
});

function displayResult(result, inputData) {
    resultPanel.classList.remove('hidden', 'APPROVED', 'REJECTED', 'ANOMALY_DETECTED', 'APPROVED_WITH_CONDITIONS');
    resultPanel.classList.add(result.decision);

    // Main Decision
    const badge = document.getElementById('decisionBadge');
    badge.textContent = result.decision.replace(/_/g, ' ');

    // Confidence
    const confidence = (result.confidence || 0) * 100;
    document.getElementById('confidenceFill').style.width = `${confidence}%`;
    document.getElementById('confidenceValue').textContent = `${confidence.toFixed(1)}%`;

    // Interpreter / Reason
    document.getElementById('decisionReason').textContent = result.explanation || result.reason;

    // Fraud Alert
    const fraudAlert = document.getElementById('fraudAlert');
    if (result.is_fraud_suspect) {
        fraudAlert.classList.remove('hidden');
    } else {
        fraudAlert.classList.add('hidden');
    }

    // Path to Success (Roadmap)
    const roadmapBox = document.getElementById('roadmapBox');
    if (result.roadmap) {
        roadmapBox.classList.remove('hidden');
        document.getElementById('roadmapMessage').textContent = result.roadmap.message;
        document.getElementById('targetFico').textContent = result.roadmap.target_fico;
        document.getElementById('targetDti').textContent = `${result.roadmap.target_dti}%`;
    } else {
        roadmapBox.classList.add('hidden');
    }

    // Alternative Offer
    const offerBox = document.getElementById('offerBox');
    if (result.alternative_offer) {
        offerBox.classList.remove('hidden');
        document.getElementById('offerMessage').textContent = result.alternative_offer.message;
        document.getElementById('offerAmount').textContent = `$${result.alternative_offer.amount.toLocaleString()}`;
    } else {
        offerBox.classList.add('hidden');
    }

    // Smart Nudge
    const nudgeBox = document.getElementById('nudgeBox');
    if (result.nudge) {
        nudgeBox.classList.remove('hidden');
        document.getElementById('nudgeMessage').textContent = result.nudge.message;
    } else {
        nudgeBox.classList.add('hidden');
    }

    // Conditions
    const conditionsBox = document.getElementById('conditionsBox');
    const conditionsList = document.getElementById('conditionsList');
    if (result.conditions && result.conditions.length > 0) {
        conditionsBox.classList.remove('hidden');
        conditionsList.innerHTML = '';
        result.conditions.forEach(c => {
            const li = document.createElement('li');
            li.textContent = c;
            conditionsList.appendChild(li);
        });
    } else {
        conditionsBox.classList.add('hidden');
    }

    // Twin Analysis
    if (result.analysis) {
        document.getElementById('twinCount').textContent = result.analysis.total_twins;
        document.getElementById('twinSuccessRate').textContent = `${(result.analysis.success_rate * 100).toFixed(1)}%`;
        document.getElementById('twinAvgSim').textContent = `${(result.analysis.avg_similarity * 100).toFixed(1)}%`;

        const twinsList = document.getElementById('topTwinsList');
        twinsList.innerHTML = '';

        result.analysis.top_twins.forEach(twin => {
            const div = document.createElement('div');
            div.className = 'twin-item';
            div.innerHTML = `
                <div class="twin-score">${(twin.similarity * 100).toFixed(0)}%</div>
                <div class="twin-info">
                    <strong>${twin.outcome}</strong>
                    <span>$${twin.requested_amount.toLocaleString()} | ${twin.fico} FICO</span>
                </div>
            `;
            twinsList.appendChild(div);
        });
    } else if (result.decision === 'ANOMALY_DETECTED') {
        // Handle anomaly specific display
        document.getElementById('twinCount').textContent = result.twins_found || 0;
        document.getElementById('twinSuccessRate').textContent = 'N/A';
        document.getElementById('twinAvgSim').textContent = 'N/A';
        document.getElementById('topTwinsList').innerHTML = '<p class="warning-text">Insufficient similarity data to show matches.</p>';
    }

    resultPanel.scrollIntoView({ behavior: 'smooth' });
}
