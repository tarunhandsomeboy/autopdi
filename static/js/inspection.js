/**
 * AUTO PDI — Live Inspection Workflow Console
 * Dynamic Checklists, Offline LocalStorage Drafts, AI Damage Scanner & Geotagged Evidence
 */

let currentInspection = null;
let activeCategory = 'All';
let timerInterval = null;
let startTime = null;

document.addEventListener('DOMContentLoaded', () => {
    const inspectionContainer = document.getElementById('inspection-workflow-container');
    if (inspectionContainer) {
        const inspectionId = inspectionContainer.dataset.inspectionId;
        initInspectionConsole(inspectionId);
    }
});

async function initInspectionConsole(inspectionId) {
    // 1. Fetch Inspection details
    const res = await AutoPDI.api(`/api/inspections/${inspectionId}`);
    if (!res.success) return;

    currentInspection = res.data;
    renderInspectionHeader(currentInspection);
    renderCategoryNavigation(currentInspection.grouped_checkpoints);
    renderCheckpointsList(currentInspection.grouped_checkpoints);
    updateProgressAndScore(currentInspection.score_preview);

    // Initialize Timer if started
    if (currentInspection.inspection.started_at) {
        startTime = new Date(currentInspection.inspection.started_at);
        startTimer();
    }

    // Bind VIN Verification
    document.getElementById('btn-verify-vin')?.addEventListener('click', () => handleVINVerification(inspectionId));
    document.getElementById('btn-start-inspection')?.addEventListener('click', () => handleStartInspection(inspectionId));
    document.getElementById('btn-complete-inspection')?.addEventListener('click', () => handleCompleteInspection(inspectionId));

    // Offline storage recovery
    loadOfflineDrafts(inspectionId);
}

function renderInspectionHeader(data) {
    const insp = data.inspection;
    const v = data.vehicle;
    const b = data.booking;

    document.getElementById('disp-vehicle-title').innerText = `${v.brand} ${v.model} ${v.variant || ''}`;
    document.getElementById('disp-vehicle-type').innerText = `${v.vehicle_type} (${v.fuel_type})`;
    document.getElementById('disp-vin').innerText = v.vin;
    document.getElementById('disp-verification-code').innerText = insp.verification_code;

    // Show/hide pre-start banner vs active console
    const vinBanner = document.getElementById('vin-verification-banner');
    const checklistSection = document.getElementById('checklist-main-section');

    if (!insp.vin_verified || !insp.started_at) {
        vinBanner.style.display = 'block';
        checklistSection.style.opacity = '0.4';
        checklistSection.style.pointerEvents = 'none';

        if (insp.vin_verified) {
            document.getElementById('vin-input-group').style.display = 'none';
            document.getElementById('vin-success-badge').style.display = 'inline-flex';
            document.getElementById('btn-start-inspection').disabled = false;
        }
    } else {
        vinBanner.style.display = 'none';
        checklistSection.style.opacity = '1';
        checklistSection.style.pointerEvents = 'auto';
        document.getElementById('btn-complete-inspection').style.display = 'inline-flex';
    }
}

function startTimer() {
    if (timerInterval) clearInterval(timerInterval);
    const timerDisplay = document.getElementById('inspection-timer-disp');
    if (!timerDisplay) return;

    timerInterval = setInterval(() => {
        const now = new Date();
        const diffMs = now - startTime;
        const totalSecs = Math.floor(diffMs / 1000);
        const hrs = String(Math.floor(totalSecs / 3600)).padStart(2, '0');
        const mins = String(Math.floor((totalSecs % 3600) / 60)).padStart(2, '0');
        const secs = String(totalSecs % 60).padStart(2, '0');
        timerDisplay.innerText = `${hrs}:${mins}:${secs}`;
    }, 1000);
}

async function handleVINVerification(inspectionId) {
    const vinInput = document.getElementById('input-verify-vin');
    const vinVal = vinInput.value.trim();

    if (!vinVal) {
        AutoPDI.toast('Please enter or scan the vehicle VIN plate.', 'warning');
        return;
    }

    const res = await AutoPDI.api(`/api/inspections/${inspectionId}/verify-vin`, {
        method: 'POST',
        body: JSON.stringify({ vin: vinVal })
    });

    if (res.success) {
        AutoPDI.toast('Vehicle VIN verified successfully ✓', 'success');
        document.getElementById('vin-input-group').style.display = 'none';
        document.getElementById('vin-success-badge').style.display = 'inline-flex';
        document.getElementById('btn-start-inspection').disabled = false;
    }
}

async function handleStartInspection(inspectionId) {
    const res = await AutoPDI.api(`/api/inspections/${inspectionId}/start`, { method: 'POST' });
    if (res.success) {
        AutoPDI.toast('Inspection workflow started! Timer running.', 'success');
        startTime = new Date();
        startTimer();
        document.getElementById('vin-verification-banner').style.display = 'none';
        const checklistSection = document.getElementById('checklist-main-section');
        checklistSection.style.opacity = '1';
        checklistSection.style.pointerEvents = 'auto';
        document.getElementById('btn-complete-inspection').style.display = 'inline-flex';
        // Refresh inspection data
        initInspectionConsole(inspectionId);
    }
}

function renderCategoryNavigation(groupedCheckpoints) {
    const navBar = document.getElementById('category-nav-bar');
    if (!navBar) return;

    const categories = ['All', ...Object.keys(groupedCheckpoints)];
    navBar.innerHTML = categories.map(cat => `
        <button type="button" class="cat-pill ${cat === activeCategory ? 'active' : ''}" 
                onclick="filterCategory('${cat}')">
            ${cat}
        </button>
    `).join('');
}

function filterCategory(cat) {
    activeCategory = cat;
    document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
    event?.target?.classList.add('active');
    renderCheckpointsList(currentInspection.grouped_checkpoints);
}

function renderCheckpointsList(groupedCheckpoints) {
    const container = document.getElementById('checkpoints-container');
    if (!container) return;

    let itemsToRender = [];
    if (activeCategory === 'All') {
        Object.entries(groupedCheckpoints).forEach(([catName, items]) => {
            itemsToRender.push(...items);
        });
    } else {
        itemsToRender = groupedCheckpoints[activeCategory] || [];
    }

    if (itemsToRender.length === 0) {
        container.innerHTML = `<div class="text-center py-5 text-muted">No items in this category.</div>`;
        return;
    }

    container.innerHTML = itemsToRender.map(cp => {
        const statusClass = cp.status === 'PASS' ? 'status-pass' : cp.status === 'ATTENTION' ? 'status-attention' : 'status-fail';
        return `
            <div class="checkpoint-card ${statusClass}" id="cp-card-${cp.id}">
                <div class="checkpoint-title">
                    <div>
                        <span class="pdi-badge pdi-badge-neutral mb-1" style="font-size: 0.68rem;">${cp.category_name}</span>
                        <div class="fw-bold">${cp.item_name}</div>
                    </div>
                    ${cp.ai_detected ? `<span class="ai-badge"><i class="bi bi-cpu me-1"></i>AI Flagged</span>` : ''}
                </div>

                <!-- Status Buttons -->
                <div class="status-btn-group">
                    <button type="button" class="status-btn ${cp.status === 'PASS' ? 'selected-pass' : ''}" 
                            onclick="updateCheckpointStatus(${cp.id}, 'PASS')">
                        <i class="bi bi-check-circle me-1"></i>PASS
                    </button>
                    <button type="button" class="status-btn ${cp.status === 'ATTENTION' ? 'selected-attention' : ''}" 
                            onclick="updateCheckpointStatus(${cp.id}, 'ATTENTION')">
                        <i class="bi bi-exclamation-triangle me-1"></i>ATTENTION
                    </button>
                    <button type="button" class="status-btn ${cp.status === 'FAIL' ? 'selected-fail' : ''}" 
                            onclick="updateCheckpointStatus(${cp.id}, 'FAIL')">
                        <i class="bi bi-x-circle me-1"></i>FAIL
                    </button>
                </div>

                <!-- Remark Input -->
                <div class="mb-2">
                    <input type="text" class="form-control-custom form-control-sm" 
                           placeholder="Add inspector remark / observation..." 
                           value="${cp.remark || ''}" 
                           onchange="updateCheckpointRemark(${cp.id}, this.value)">
                </div>

                <!-- Action Toolbar: Camera Upload & AI Analyze -->
                <div class="d-flex justify-content-between align-items-center mt-2">
                    <div class="d-flex gap-2">
                        <label class="btn-camera">
                            <i class="bi bi-camera-fill"></i> Add Photo Evidence
                            <input type="file" accept="image/*" style="display: none;" onchange="uploadCheckpointPhoto(${cp.id}, this)">
                        </label>
                    </div>

                    ${(cp.media && cp.media.length > 0) ? `
                        <button type="button" class="btn-ai-analyze" onclick="triggerAIAnalysis(${cp.id}, '${cp.media[0].file_url}')">
                            <i class="bi bi-stars"></i> Run AI Analyze
                        </button>
                    ` : ''}
                </div>

                <!-- Media Thumbnails Preview -->
                ${(cp.media && cp.media.length > 0) ? `
                    <div class="media-preview-container">
                        ${cp.media.map(m => `
                            <div class="media-thumbnail-card" title="Captured: ${m.captured_at}">
                                <img src="${m.file_url}" alt="Evidence" onerror="this.src='/static/images/default-avatar.png'">
                            </div>
                        `).join('')}
                    </div>
                ` : ''}

                <!-- AI Finding Callout (If Present) -->
                ${renderAIFindingsForCheckpoint(cp.id)}
            </div>
        `;
    }).join('');
}

function renderAIFindingsForCheckpoint(checkpointId) {
    const findings = (currentInspection.ai_findings || []).filter(f => f.checkpoint_id === checkpointId);
    if (findings.length === 0) return '';

    return findings.map(f => `
        <div class="ai-finding-callout">
            <div class="ai-finding-header">
                <div class="d-flex align-items-center gap-2">
                    <span class="ai-badge"><i class="bi bi-robot me-1"></i>AI-Assisted Finding</span>
                    <span class="ai-confidence-pill">${f.confidence}% Confidence</span>
                </div>
                <span class="pdi-badge ${f.severity === 'LOW' ? 'pdi-badge-warning' : 'pdi-badge-danger'}">${f.severity} SEVERITY</span>
            </div>
            <strong class="d-block mb-1 text-dark">${f.finding_type}</strong>
            <p class="small text-muted mb-2">${f.description}</p>
            <div class="small fw-bold text-muted mb-1" style="font-size:0.75rem;">
                <i class="bi bi-shield-lock me-1 text-primary"></i>Requires Inspector Verification:
            </div>
            <div class="ai-actions-row">
                <button type="button" class="btn btn-pdi-success btn-sm ${f.inspector_confirmation === 'CONFIRMED' ? 'active' : ''}" 
                        onclick="confirmAIFinding(${f.id}, 'CONFIRM')">
                    <i class="bi bi-check2-circle me-1"></i>${f.inspector_confirmation === 'CONFIRMED' ? 'Confirmed ✓' : 'Confirm Finding'}
                </button>
                <button type="button" class="btn btn-outline-secondary btn-sm" 
                        onclick="confirmAIFinding(${f.id}, 'REJECT')">
                    <i class="bi bi-x-circle me-1"></i>Reject Finding
                </button>
            </div>
        </div>
    `).join('');
}

async function updateCheckpointStatus(checkpointId, status) {
    const inspectionId = currentInspection.inspection.id;

    // Save to LocalStorage immediately
    saveOfflineDraft(checkpointId, { status });

    const res = await AutoPDI.api(`/api/inspections/${inspectionId}/checkpoint`, {
        method: 'PUT',
        body: JSON.stringify({ checkpoint_id: checkpointId, status })
    });

    if (res.success) {
        updateLocalCheckpointData(checkpointId, { status });
        updateProgressAndScore(res.data.score_preview);
    }
}

async function updateCheckpointRemark(checkpointId, remark) {
    const inspectionId = currentInspection.inspection.id;
    saveOfflineDraft(checkpointId, { remark });

    const res = await AutoPDI.api(`/api/inspections/${inspectionId}/checkpoint`, {
        method: 'PUT',
        body: JSON.stringify({ checkpoint_id: checkpointId, remark })
    });

    if (res.success) {
        updateLocalCheckpointData(checkpointId, { remark });
    }
}

async function uploadCheckpointPhoto(checkpointId, inputEl) {
    if (!inputEl.files || !inputEl.files[0]) return;
    const file = inputEl.files[0];
    const inspectionId = currentInspection.inspection.id;

    AutoPDI.toast('Uploading evidence & capturing GPS coordinates...', 'info');

    const geo = await AutoPDI.getGeolocation();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('checkpoint_id', checkpointId);
    if (geo.latitude) formData.append('latitude', geo.latitude);
    if (geo.longitude) formData.append('longitude', geo.longitude);

    const res = await AutoPDI.api(`/api/inspections/${inspectionId}/photo`, {
        method: 'POST',
        body: formData
    });

    if (res.success) {
        AutoPDI.toast('Photo evidence saved with timestamp and GPS.', 'success');
        // Refresh inspection data to display image thumbnail
        const refreshRes = await AutoPDI.api(`/api/inspections/${inspectionId}`);
        if (refreshRes.success) {
            currentInspection = refreshRes.data;
            renderCheckpointsList(currentInspection.grouped_checkpoints);
        }
    }
}

async function triggerAIAnalysis(checkpointId, imageUrl) {
    const inspectionId = currentInspection.inspection.id;
    AutoPDI.toast('Analyzing image through Computer Vision engine...', 'info');

    const res = await AutoPDI.api(`/api/inspections/${inspectionId}/ai-analysis`, {
        method: 'POST',
        body: JSON.stringify({ checkpoint_id: checkpointId, image_url: imageUrl })
    });

    if (res.success) {
        AutoPDI.toast('AI Damage Analysis complete! Please confirm findings.', 'success');
        const refreshRes = await AutoPDI.api(`/api/inspections/${inspectionId}`);
        if (refreshRes.success) {
            currentInspection = refreshRes.data;
            renderCheckpointsList(currentInspection.grouped_checkpoints);
            updateProgressAndScore(currentInspection.score_preview);
        }
    }
}

async function confirmAIFinding(findingId, action) {
    const inspectionId = currentInspection.inspection.id;
    const res = await AutoPDI.api(`/api/inspections/${inspectionId}/ai-confirm`, {
        method: 'POST',
        body: JSON.stringify({ finding_id: findingId, action })
    });

    if (res.success) {
        AutoPDI.toast(`AI finding ${action.toLowerCase()}ed.`, 'success');
        const refreshRes = await AutoPDI.api(`/api/inspections/${inspectionId}`);
        if (refreshRes.success) {
            currentInspection = refreshRes.data;
            renderCheckpointsList(currentInspection.grouped_checkpoints);
            updateProgressAndScore(currentInspection.score_preview);
        }
    }
}

function updateLocalCheckpointData(checkpointId, updates) {
    Object.values(currentInspection.grouped_checkpoints).forEach(items => {
        const target = items.find(cp => cp.id === checkpointId);
        if (target) {
            Object.assign(target, updates);
        }
    });
    renderCheckpointsList(currentInspection.grouped_checkpoints);
}

function updateProgressAndScore(scorePreview) {
    if (!scorePreview) return;
    const stats = scorePreview.stats || { pass: 0, attention: 0, fail: 0, total: 1 };
    const totalDone = stats.pass + stats.attention + stats.fail;
    const pct = Math.round((totalDone / (stats.total || 1)) * 100);

    const progBar = document.getElementById('inspection-progress-bar');
    if (progBar) {
        progBar.style.width = `${pct}%`;
        progBar.innerText = `${pct}%`;
    }

    const scoreDisp = document.getElementById('header-live-score');
    if (scoreDisp) {
        scoreDisp.innerText = scorePreview.overall_score;
    }

    const gaugeCircle = document.getElementById('header-gauge-circle');
    if (gaugeCircle) {
        gaugeCircle.className = `gauge-circle ${scorePreview.overall_score >= 90 ? 'status-green' : scorePreview.overall_score >= 75 ? 'status-yellow' : 'status-red'}`;
    }
}

async function handleCompleteInspection(inspectionId) {
    if (!confirm('Are you ready to complete this inspection and generate the official PDF report?')) return;

    const completeBtn = document.getElementById('btn-complete-inspection');
    completeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating Report...';
    completeBtn.disabled = true;

    const res = await AutoPDI.api(`/api/inspections/${inspectionId}/complete`, { method: 'POST' });

    if (res.success) {
        AutoPDI.toast('Inspection completed successfully! Report generated.', 'success');
        // Clear local storage drafts
        localStorage.removeItem(`autopdi_draft_${inspectionId}`);
        setTimeout(() => {
            window.location.href = `/customer/report/${inspectionId}`;
        }, 1000);
    } else {
        completeBtn.innerHTML = '<i class="bi bi-check-all me-1"></i>Complete Inspection';
        completeBtn.disabled = false;
    }
}

// Offline Draft Storage in LocalStorage
function saveOfflineDraft(checkpointId, data) {
    if (!currentInspection) return;
    const key = `autopdi_draft_${currentInspection.inspection.id}`;
    const draft = JSON.parse(localStorage.getItem(key) || '{}');
    draft[checkpointId] = { ...(draft[checkpointId] || {}), ...data, timestamp: Date.now() };
    localStorage.setItem(key, JSON.stringify(draft));
}

function loadOfflineDrafts(inspectionId) {
    const key = `autopdi_draft_${inspectionId}`;
    const draft = JSON.parse(localStorage.getItem(key) || '{}');
    const draftKeys = Object.keys(draft);
    if (draftKeys.length > 0) {
        console.log(`Loaded ${draftKeys.length} offline checkpoint drafts from localStorage.`);
    }
}
