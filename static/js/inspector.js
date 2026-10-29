/**
 * AUTO PDI — Inspector Portal Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('inspector-dashboard-container')) {
        loadInspectorDashboard();
    }

    if (document.getElementById('inspector-requests-container')) {
        loadInspectorRequests();
    }

    if (document.getElementById('inspector-profile-container')) {
        loadInspectorProfile();
    }
});

async function loadInspectorDashboard() {
    const res = await AutoPDI.api('/api/inspector/dashboard');
    if (!res.success) return;

    const data = res.data;
    document.getElementById('stat-today-count').innerText = data.stats.today_inspections;
    document.getElementById('stat-pending-count').innerText = data.stats.pending_requests;
    document.getElementById('stat-completed-count').innerText = data.stats.completed_inspections;
    document.getElementById('stat-earnings').innerText = AutoPDI.formatINR(data.stats.earnings);
    document.getElementById('stat-trust-score').innerText = `${data.stats.trust_score}/100`;

    // Render Pending Requests Card / Table
    const reqContainer = document.getElementById('dashboard-requests-list');
    if (reqContainer) {
        if (data.pending_requests.length === 0) {
            reqContainer.innerHTML = `<p class="text-muted small text-center py-4">No pending inspection requests.</p>`;
        } else {
            reqContainer.innerHTML = data.pending_requests.map(b => `
                <div class="pdi-card mb-3 p-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div>
                            <span class="pdi-badge pdi-badge-primary mb-1">${b.inspection_type} PDI</span>
                            <h6 class="fw-bold mb-1">${b.vehicle ? b.vehicle.brand + ' ' + b.vehicle.model : 'Vehicle'}</h6>
                            <p class="text-muted small mb-1"><i class="bi bi-geo-alt me-1"></i>${b.showroom ? b.showroom.name : 'Showroom'}</p>
                            <small class="text-muted"><i class="bi bi-clock me-1"></i>${b.scheduled_date} at ${b.scheduled_time}</small>
                        </div>
                        <div class="text-end">
                            <span class="fw-bold fs-5 text-primary">${AutoPDI.formatINR(b.price)}</span>
                            <div class="mt-2 d-flex gap-2">
                                <button class="btn btn-pdi-success btn-sm" onclick="acceptBooking(${b.id})">Accept</button>
                                <button class="btn btn-outline-danger btn-sm" onclick="rejectBooking(${b.id})">Decline</button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }

    // Render Active Inspections
    const activeContainer = document.getElementById('dashboard-active-inspections');
    if (activeContainer) {
        if (data.active_inspections.length === 0) {
            activeContainer.innerHTML = `<p class="text-muted small text-center py-3">No inspections currently in progress.</p>`;
        } else {
            activeContainer.innerHTML = data.active_inspections.map(insp => `
                <div class="pdi-card pdi-card-hover border-primary mb-3 p-3 d-flex justify-content-between align-items-center">
                    <div>
                        <span class="pdi-badge pdi-badge-warning mb-1">IN PROGRESS</span>
                        <h6 class="fw-bold mb-1">Inspection Code: ${insp.verification_code}</h6>
                        <small class="text-muted">VIN Verified: ${insp.vin_verified ? 'Yes ✓' : 'Pending'}</small>
                    </div>
                    <a href="/inspector/inspection/${insp.id}" class="btn btn-pdi-primary btn-sm">
                        <i class="bi bi-play-circle me-1"></i>Open Inspection Console
                    </a>
                </div>
            `).join('');
        }
    }
}

async function loadInspectorRequests() {
    const res = await AutoPDI.api('/api/bookings');
    const container = document.getElementById('inspector-all-requests');
    if (!container || !res.success) return;

    const bookings = res.data;
    if (bookings.length === 0) {
        container.innerHTML = `<div class="text-center py-5 text-muted">No booking history available.</div>`;
        return;
    }

    container.innerHTML = bookings.map(b => `
        <div class="pdi-card mb-3 p-4">
            <div class="d-flex justify-content-between align-items-start mb-3">
                <div>
                    <div class="d-flex align-items-center gap-2 mb-2">
                        <span class="pdi-badge ${b.status === 'ACCEPTED' ? 'pdi-badge-success' : b.status === 'IN_PROGRESS' ? 'pdi-badge-warning' : 'pdi-badge-primary'}">${b.status}</span>
                        <span class="pdi-badge pdi-badge-neutral">${b.inspection_type}</span>
                    </div>
                    <h5 class="fw-bold mb-1">${b.vehicle ? b.vehicle.brand + ' ' + b.vehicle.model : 'Vehicle'}</h5>
                    <p class="text-muted small mb-1"><i class="bi bi-geo-alt me-1"></i>${b.showroom ? b.showroom.name + ' (' + b.showroom.city + ')' : ''}</p>
                    <div class="small text-muted">
                        <i class="bi bi-calendar me-1"></i>${b.scheduled_date} at ${b.scheduled_time} • 
                        <i class="bi bi-person me-1"></i>Customer: ${b.customer_name || 'Customer'} (${b.customer_phone || ''})
                    </div>
                </div>
                <div class="text-end">
                    <div class="fs-4 fw-bold text-primary mb-2">${AutoPDI.formatINR(b.price)}</div>
                    ${b.status === 'REQUESTED' ? `
                        <div class="d-flex gap-2">
                            <button class="btn btn-pdi-success btn-sm" onclick="acceptBooking(${b.id})"><i class="bi bi-check-lg me-1"></i>Accept</button>
                            <button class="btn btn-outline-danger btn-sm" onclick="rejectBooking(${b.id})">Reject</button>
                        </div>
                    ` : b.status === 'ACCEPTED' || b.status === 'IN_PROGRESS' ? `
                        <a href="/inspector/inspection/${b.inspection_id || b.id}" class="btn btn-pdi-primary btn-sm">
                            <i class="bi bi-arrow-right-circle me-1"></i>Launch Inspection
                        </a>
                    ` : `<span class="text-muted small">Completed</span>`}
                </div>
            </div>
            ${b.notes ? `<div class="bg-light p-2 rounded small text-muted"><b>Customer Note:</b> ${b.notes}</div>` : ''}
        </div>
    `).join('');
}

async function acceptBooking(bookingId) {
    const res = await AutoPDI.api(`/api/bookings/${bookingId}/accept`, { method: 'POST' });
    if (res.success) {
        AutoPDI.toast('Booking accepted! Inspection workspace ready.', 'success');
        setTimeout(() => window.location.reload(), 600);
    }
}

async function rejectBooking(bookingId) {
    if (!confirm('Are you sure you want to decline this inspection request?')) return;
    const res = await AutoPDI.api(`/api/bookings/${bookingId}/reject`, { method: 'POST' });
    if (res.success) {
        AutoPDI.toast('Booking request declined.', 'info');
        setTimeout(() => window.location.reload(), 600);
    }
}

async function loadInspectorProfile() {
    const res = await AutoPDI.api('/api/inspector/dashboard');
    if (!res.success) return;
    const insp = res.data.profile;

    document.getElementById('prof-bio').value = insp.bio || '';
    document.getElementById('prof-experience').value = insp.experience_years;
    document.getElementById('prof-spec').value = insp.specialization || '';
    document.getElementById('prof-price-std').value = insp.price_standard;
    document.getElementById('prof-price-prem').value = insp.price_premium;
    document.getElementById('prof-availability').value = insp.availability_status;

    // Render Equipment
    const eqContainer = document.getElementById('profile-equipment-list');
    if (eqContainer) {
        eqContainer.innerHTML = (insp.equipment || []).map(eq => `
            <div class="d-flex justify-content-between align-items-center p-2 mb-2 bg-light rounded border">
                <div>
                    <strong>${eq.equipment_name}</strong>
                    <small class="d-block text-muted">Type: ${eq.equipment_type} | Serial: ${eq.serial_number || 'N/A'}</small>
                </div>
                <span class="pdi-badge ${eq.verification_status === 'VERIFIED' ? 'pdi-badge-success' : 'pdi-badge-warning'}">
                    ${eq.verification_status}
                </span>
            </div>
        `).join('');
    }

    // Add Equipment Handler
    document.getElementById('add-equipment-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const equipment_name = document.getElementById('new_eq_name').value.trim();
        const equipment_type = document.getElementById('new_eq_type').value;
        const serial_number = document.getElementById('new_eq_serial').value.trim();

        const addRes = await AutoPDI.api('/api/inspector/equipment', {
            method: 'POST',
            body: JSON.stringify({ equipment_name, equipment_type, serial_number })
        });

        if (addRes.success) {
            AutoPDI.toast('Equipment added. Pending admin verification.', 'success');
            loadInspectorProfile();
        }
    });
}
