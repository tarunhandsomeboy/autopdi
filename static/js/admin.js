/**
 * AUTO PDI — Admin Console & Chart.js Visualizations
 */

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('admin-dashboard-container')) {
        loadAdminDashboard();
    }

    if (document.getElementById('admin-inspectors-container')) {
        loadAdminInspectorsList();
    }
});

async function loadAdminDashboard() {
    const res = await AutoPDI.api('/api/admin/dashboard');
    if (!res.success) return;

    const { kpis, charts, top_inspectors } = res.data;

    // Render KPI Metrics
    document.getElementById('kpi-customers').innerText = kpis.total_customers;
    document.getElementById('kpi-inspectors').innerText = kpis.total_inspectors;
    document.getElementById('kpi-pending-inspectors').innerText = kpis.pending_inspectors;
    document.getElementById('kpi-bookings').innerText = kpis.total_bookings;
    document.getElementById('kpi-active-inspections').innerText = kpis.active_inspections;
    document.getElementById('kpi-completed-inspections').innerText = kpis.completed_inspections;
    document.getElementById('kpi-revenue').innerText = AutoPDI.formatINR(kpis.total_revenue);
    document.getElementById('kpi-rating').innerText = `★ ${kpis.avg_rating}`;

    // Render 5 Dynamic Chart.js charts
    renderAdminCharts(charts);

    // Render Top Inspectors Leaderboard
    const leaderboard = document.getElementById('admin-top-inspectors-list');
    if (leaderboard) {
        leaderboard.innerHTML = top_inspectors.map((insp, idx) => `
            <div class="d-flex justify-content-between align-items-center p-3 mb-2 bg-light rounded border">
                <div class="d-flex align-items-center gap-3">
                    <span class="badge bg-primary rounded-circle" style="width:28px; height:28px; display:flex; align-items:center; justify-content:center;">#${idx + 1}</span>
                    <div>
                        <strong class="d-block text-dark">${insp.name}</strong>
                        <small class="text-muted"><i class="bi bi-star-fill text-warning me-1"></i>${insp.rating} • ${insp.inspections} completed PDIs</small>
                    </div>
                </div>
                <span class="trust-score-pill">Trust: ${insp.trust_score}/100</span>
            </div>
        `).join('');
    }
}

function renderAdminCharts(charts) {
    if (typeof Chart === 'undefined') return;

    // 1. Monthly Trend Chart (Line)
    const trendCtx = document.getElementById('chart-monthly-trend')?.getContext('2d');
    if (trendCtx) {
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: charts.monthly_trend.labels,
                datasets: [{
                    label: 'PDI Bookings',
                    data: charts.monthly_trend.bookings,
                    borderColor: '#2563EB',
                    backgroundColor: 'rgba(37, 99, 235, 0.08)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3,
                    pointBackgroundColor: '#2563EB',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#F1F5F9' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 2. Booking Status (Doughnut)
    const statusCtx = document.getElementById('chart-booking-status')?.getContext('2d');
    if (statusCtx) {
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(charts.booking_status),
                datasets: [{
                    data: Object.values(charts.booking_status),
                    backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#6366F1', '#EF4444'],
                    borderWidth: 2,
                    borderColor: '#FFFFFF'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { boxWidth: 12 } } }
            }
        });
    }

    // 3. Vehicle Types Distribution (Pie)
    const vTypeCtx = document.getElementById('chart-vehicle-types')?.getContext('2d');
    if (vTypeCtx) {
        new Chart(vTypeCtx, {
            type: 'pie',
            data: {
                labels: Object.keys(charts.vehicle_types),
                datasets: [{
                    data: Object.values(charts.vehicle_types),
                    backgroundColor: ['#0F172A', '#06B6D4', '#10B981'],
                    borderWidth: 2,
                    borderColor: '#FFFFFF'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { boxWidth: 12 } } }
            }
        });
    }

    // 4. Standard vs Premium Packages (Bar)
    const pkgCtx = document.getElementById('chart-packages')?.getContext('2d');
    if (pkgCtx) {
        new Chart(pkgCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(charts.packages),
                datasets: [{
                    data: Object.values(charts.packages),
                    backgroundColor: ['#94A3B8', '#2563EB'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#F1F5F9' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 5. Readiness Verdicts (Doughnut)
    const verdictCtx = document.getElementById('chart-verdicts')?.getContext('2d');
    if (verdictCtx) {
        new Chart(verdictCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(charts.verdicts),
                datasets: [{
                    data: Object.values(charts.verdicts),
                    backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
                    borderWidth: 2,
                    borderColor: '#FFFFFF'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { boxWidth: 12 } } }
            }
        });
    }
}

/**
 * Admin Inspector Approval Management
 */
async function loadAdminInspectorsList() {
    const res = await AutoPDI.api('/api/admin/inspectors');
    const container = document.getElementById('admin-inspectors-table-body');
    if (!container || !res.success) return;

    container.innerHTML = res.data.map(insp => `
        <tr>
            <td>
                <div class="d-flex align-items-center gap-2">
                    <img src="${insp.profile_image}" class="rounded-circle" width="36" height="36" onerror="this.src='/static/images/default-avatar.png'">
                    <div>
                        <strong>${insp.name}</strong>
                        <small class="d-block text-muted">${insp.email}</small>
                    </div>
                </div>
            </td>
            <td>${insp.experience_years} Years</td>
            <td><i class="bi bi-star-fill text-warning me-1"></i>${insp.rating} (${insp.total_inspections})</td>
            <td><span class="trust-score-pill">${insp.trust_score}/100</span></td>
            <td>
                <span class="pdi-badge ${insp.verification_status === 'VERIFIED' ? 'pdi-badge-success' : insp.verification_status === 'PENDING' ? 'pdi-badge-warning' : 'pdi-badge-danger'}">
                    ${insp.verification_status}
                </span>
            </td>
            <td>
                <div class="d-flex gap-1">
                    ${insp.verification_status === 'PENDING' ? `
                        <button class="btn btn-pdi-success btn-sm" onclick="approveInspector(${insp.id})">Approve</button>
                        <button class="btn btn-outline-danger btn-sm" onclick="rejectInspector(${insp.id})">Reject</button>
                    ` : insp.verification_status === 'VERIFIED' ? `
                        <button class="btn btn-outline-warning btn-sm" onclick="suspendInspector(${insp.id})">Suspend</button>
                    ` : `
                        <button class="btn btn-outline-success btn-sm" onclick="approveInspector(${insp.id})">Re-Activate</button>
                    `}
                    <button class="btn btn-outline-secondary btn-sm" onclick="viewInspectorDetails(${insp.id}, ${JSON.stringify(insp).replace(/"/g, '&quot;')})">
                        <i class="bi bi-eye"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

async function approveInspector(id) {
    const res = await AutoPDI.api(`/api/admin/inspectors/${id}/approve`, { method: 'PUT' });
    if (res.success) {
        AutoPDI.toast('Inspector approved successfully!', 'success');
        loadAdminInspectorsList();
    }
}

async function rejectInspector(id) {
    if (!confirm('Are you sure you want to reject this inspector application?')) return;
    const res = await AutoPDI.api(`/api/admin/inspectors/${id}/reject`, { method: 'PUT' });
    if (res.success) {
        AutoPDI.toast('Inspector application rejected.', 'info');
        loadAdminInspectorsList();
    }
}

async function suspendInspector(id) {
    if (!confirm('Are you sure you want to suspend this inspector account?')) return;
    const res = await AutoPDI.api(`/api/admin/inspectors/${id}/suspend`, { method: 'PUT' });
    if (res.success) {
        AutoPDI.toast('Inspector suspended.', 'warning');
        loadAdminInspectorsList();
    }
}

function viewInspectorDetails(id, data) {
    const modalContent = document.getElementById('inspector-modal-content');
    if (!modalContent) return;

    modalContent.innerHTML = `
        <h5>${data.name}</h5>
        <p class="text-muted small">${data.bio || 'No bio provided.'}</p>
        <hr>
        <h6 class="fw-bold">Equipment Inventory (${(data.equipment || []).length})</h6>
        ${(data.equipment || []).map(eq => `
            <div class="d-flex justify-content-between align-items-center p-2 mb-1 bg-light rounded small">
                <span>${eq.equipment_name} (${eq.equipment_type})</span>
                <button class="btn btn-sm btn-outline-success" onclick="verifyEquipment(${eq.id})">Verify Tool ✓</button>
            </div>
        `).join('') || '<small class="text-muted">No equipment registered.</small>'}

        <h6 class="fw-bold mt-3">Certifications (${(data.certifications || []).length})</h6>
        ${(data.certifications || []).map(c => `
            <div class="d-flex justify-content-between align-items-center p-2 mb-1 bg-light rounded small">
                <span>${c.certificate_name} - ${c.issuer}</span>
                <button class="btn btn-sm btn-outline-success" onclick="verifyCertification(${c.id})">Verify Cert ✓</button>
            </div>
        `).join('') || '<small class="text-muted">No certifications registered.</small>'}
    `;

    const modalEl = document.getElementById('inspectorDetailModal');
    if (modalEl && window.bootstrap) {
        new bootstrap.Modal(modalEl).show();
    }
}

async function verifyEquipment(eqId) {
    const res = await AutoPDI.api(`/api/admin/equipment/${eqId}/verify`, { method: 'PUT' });
    if (res.success) {
        AutoPDI.toast('Equipment verified ✓', 'success');
        loadAdminInspectorsList();
    }
}

async function verifyCertification(certId) {
    const res = await AutoPDI.api(`/api/admin/certifications/${certId}/verify`, { method: 'PUT' });
    if (res.success) {
        AutoPDI.toast('Certification verified ✓', 'success');
        loadAdminInspectorsList();
    }
}
