/**
 * AUTO PDI — Customer Portal & 6-Step Booking Wizard Logic
 */

let bookingState = {
    step: 1,
    vehicle_id: null,
    vehicle_data: null,
    showroom_id: null,
    showroom_data: null,
    scheduled_date: null,
    scheduled_time: '10:00',
    package: 'PREMIUM',
    inspector_id: null,
    inspector_data: null,
    notes: '',
    price: 2499.00
};

document.addEventListener('DOMContentLoaded', () => {
    // Check if on Customer Dashboard
    if (document.getElementById('customer-dashboard-container')) {
        loadCustomerDashboard();
    }

    // Check if on Booking Wizard
    if (document.getElementById('booking-wizard-container')) {
        initBookingWizard();
    }

    // Check if on Vehicles Page
    if (document.getElementById('vehicles-page-container')) {
        loadVehiclesPage();
    }

    // Check if on Bookings Page
    if (document.getElementById('bookings-page-container')) {
        loadBookingsPage();
    }
});

/**
 * Load Customer Dashboard
 */
async function loadCustomerDashboard() {
    const res = await AutoPDI.api('/api/customer/dashboard');
    if (!res.success) return;

    const data = res.data;
    document.getElementById('stat-vehicles-count').innerText = data.stats.total_vehicles;
    document.getElementById('stat-upcoming-count').innerText = data.stats.upcoming_pdi_count;
    document.getElementById('stat-completed-count').innerText = data.stats.completed_pdi_count;
    document.getElementById('stat-reports-count').innerText = data.stats.reports_count;

    // Render upcoming bookings
    const upcomingContainer = document.getElementById('upcoming-bookings-list');
    if (upcomingContainer) {
        if (data.upcoming_bookings.length === 0) {
            upcomingContainer.innerHTML = `
                <div class="text-center py-4 text-muted">
                    <i class="bi bi-calendar2-check fs-2 d-block mb-2 text-primary opacity-50"></i>
                    <p class="mb-0 font-weight-500">No active PDI appointments.</p>
                    <a href="/customer/book" class="btn btn-pdi-primary btn-sm mt-3">Book New Inspection</a>
                </div>
            `;
        } else {
            upcomingContainer.innerHTML = data.upcoming_bookings.map(b => `
                <div class="pdi-card pdi-card-hover mb-3 p-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <span class="pdi-badge pdi-badge-primary mb-2">${b.inspection_type} PDI</span>
                            <h5 class="mb-1 font-weight-bold">${b.vehicle ? b.vehicle.brand + ' ' + b.vehicle.model : 'Vehicle'}</h5>
                            <p class="text-muted small mb-2"><i class="bi bi-geo-alt me-1"></i>${b.showroom ? b.showroom.name : 'Showroom'}</p>
                            <div class="small text-muted">
                                <i class="bi bi-clock me-1"></i>${b.scheduled_date} at ${b.scheduled_time}
                                <span class="ms-3"><i class="bi bi-person-badge me-1"></i>${b.inspector_name || 'Assigned Inspector'}</span>
                            </div>
                        </div>
                        <div class="text-end">
                            <span class="pdi-badge ${b.status === 'IN_PROGRESS' ? 'pdi-badge-warning' : 'pdi-badge-primary'}">${b.status}</span>
                            <div class="mt-3">
                                <span class="fw-bold fs-6 text-primary">${AutoPDI.formatINR(b.price)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }

    // Render Recent Reports
    const reportsContainer = document.getElementById('recent-reports-list');
    if (reportsContainer) {
        if (data.reports.length === 0) {
            reportsContainer.innerHTML = `<p class="text-muted small text-center py-3">No completed inspection reports yet.</p>`;
        } else {
            reportsContainer.innerHTML = data.reports.map(r => `
                <div class="pdi-card pdi-card-hover mb-3 p-3 d-flex justify-content-between align-items-center">
                    <div>
                        <div class="d-flex align-items-center gap-2 mb-1">
                            <span class="pdi-badge ${r.final_status === 'DELIVERY_READY' ? 'pdi-badge-success' : 'pdi-badge-warning'}">
                                ${r.final_status.replace('_', ' ')}
                            </span>
                            <span class="small text-muted">Code: <b>${r.verification_code}</b></span>
                        </div>
                        <h6 class="mb-0 fw-bold">${r.vehicle_name}</h6>
                        <small class="text-muted">${r.date}</small>
                    </div>
                    <div class="d-flex align-items-center gap-3">
                        <div class="text-center">
                            <span class="fs-5 fw-bold text-dark">${r.overall_score}</span>
                            <small class="d-block text-muted" style="font-size: 0.65rem;">SCORE</small>
                        </div>
                        <a href="/customer/report/${r.inspection_id}" class="btn btn-pdi-secondary btn-sm">
                            <i class="bi bi-file-earmark-text me-1"></i>View
                        </a>
                        <a href="/reports/${r.inspection_id}/pdf" class="btn btn-pdi-primary btn-sm" target="_blank">
                            <i class="bi bi-download"></i>
                        </a>
                    </div>
                </div>
            `).join('');
        }
    }
}

/**
 * 6-Step Interactive Booking Wizard
 */
async function initBookingWizard() {
    // 1. Fetch user's existing vehicles and showrooms
    const [vehRes, showRes] = await Promise.all([
        AutoPDI.api('/api/vehicles'),
        AutoPDI.api('/api/showrooms')
    ]);

    renderVehicleSelection(vehRes.data || []);
    renderShowroomSelection(showRes.data || []);

    // Stepper Navigation Buttons
    document.getElementById('btn-next-step')?.addEventListener('click', handleNextStep);
    document.getElementById('btn-prev-step')?.addEventListener('click', handlePrevStep);

    // Package Selection Cards
    document.querySelectorAll('.package-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.package-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            bookingState.package = card.dataset.package;
            bookingState.price = bookingState.package === 'PREMIUM' ? 2499.00 : 1499.00;
        });
    });

    // Add Vehicle Modal Form inside Step 1
    const newVehForm = document.getElementById('wizard-new-vehicle-form');
    if (newVehForm) {
        newVehForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const brand = document.getElementById('v_brand').value.trim();
            const model = document.getElementById('v_model').value.trim();
            const variant = document.getElementById('v_variant').value.trim();
            const fuel_type = document.getElementById('v_fuel').value;
            const vehicle_type = document.getElementById('v_type').value;
            const vin = document.getElementById('v_vin').value.trim();
            const registration_number = document.getElementById('v_reg').value.trim();

            const res = await AutoPDI.api('/api/vehicles', {
                method: 'POST',
                body: JSON.stringify({ brand, model, variant, fuel_type, vehicle_type, vin, registration_number })
            });

            if (res.success) {
                AutoPDI.toast('Vehicle saved successfully!', 'success');
                // Refresh vehicle list
                const refreshed = await AutoPDI.api('/api/vehicles');
                renderVehicleSelection(refreshed.data || []);
                // Select newly created vehicle
                selectVehicle(res.data.id, res.data);
                // Close modal if bootstrap is active
                const modalEl = document.getElementById('addVehicleModal');
                if (modalEl && window.bootstrap) {
                    bootstrap.Modal.getInstance(modalEl)?.hide();
                }
            }
        });
    }
}

function renderVehicleSelection(vehicles) {
    const listEl = document.getElementById('wizard-vehicle-list');
    if (!listEl) return;

    if (vehicles.length === 0) {
        listEl.innerHTML = `
            <div class="col-12 text-center py-4">
                <p class="text-muted">No vehicles added yet. Please add your new vehicle details below.</p>
                <button type="button" class="btn btn-pdi-primary" data-bs-toggle="modal" data-bs-target="#addVehicleModal">
                    <i class="bi bi-plus-circle me-1"></i>Add New Vehicle
                </button>
            </div>
        `;
        return;
    }

    listEl.innerHTML = vehicles.map(v => `
        <div class="col-md-6 mb-3">
            <div class="pdi-card pdi-card-hover cursor-pointer wizard-select-card ${bookingState.vehicle_id === v.id ? 'border-primary bg-light' : ''}" 
                 onclick="selectVehicle(${v.id}, ${JSON.stringify(v).replace(/"/g, '&quot;')})">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <span class="pdi-badge pdi-badge-primary mb-2">${v.vehicle_type} (${v.fuel_type})</span>
                        <h5 class="fw-bold mb-1">${v.brand} ${v.model}</h5>
                        <p class="text-muted small mb-1">${v.variant || ''}</p>
                        <small class="text-muted font-monospace">VIN: ${v.vin.startsWith('PENDING-') ? '<span class="badge bg-warning-subtle text-dark border border-warning-subtle">Pending Allotment</span>' : v.vin}</small>
                    </div>
                    <i class="bi ${bookingState.vehicle_id === v.id ? 'bi-check-circle-fill text-primary' : 'bi-circle'} fs-4"></i>
                </div>
            </div>
        </div>
    `).join('');

    // Auto-select first vehicle if none selected
    if (!bookingState.vehicle_id && vehicles.length > 0) {
        selectVehicle(vehicles[0].id, vehicles[0]);
    }
}

function selectVehicle(id, data) {
    bookingState.vehicle_id = id;
    bookingState.vehicle_data = data;
    document.querySelectorAll('.wizard-select-card').forEach(c => c.classList.remove('border-primary', 'bg-light'));
    event?.currentTarget?.classList.add('border-primary', 'bg-light');
}

function renderShowroomSelection(showrooms) {
    const listEl = document.getElementById('wizard-showroom-list');
    if (!listEl) return;

    listEl.innerHTML = showrooms.map(s => `
        <div class="col-md-6 mb-3">
            <div class="pdi-card pdi-card-hover cursor-pointer showroom-select-card ${bookingState.showroom_id === s.id ? 'border-primary bg-light' : ''}" 
                 onclick="selectShowroom(${s.id}, ${JSON.stringify(s).replace(/"/g, '&quot;')})">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="fw-bold mb-1">${s.name}</h6>
                        <p class="text-muted small mb-1"><i class="bi bi-geo-alt me-1"></i>${s.address}, ${s.city}</p>
                        <small class="text-muted"><i class="bi bi-telephone me-1"></i>${s.contact_number || 'N/A'}</small>
                    </div>
                    <i class="bi ${bookingState.showroom_id === s.id ? 'bi-check-circle-fill text-primary' : 'bi-circle'} fs-4"></i>
                </div>
            </div>
        </div>
    `).join('');

    if (!bookingState.showroom_id && showrooms.length > 0) {
        selectShowroom(showrooms[0].id, showrooms[0]);
    }
}

function selectShowroom(id, data) {
    bookingState.showroom_id = id;
    bookingState.showroom_data = data;
    document.querySelectorAll('.showroom-select-card').forEach(c => c.classList.remove('border-primary', 'bg-light'));
    event?.currentTarget?.classList.add('border-primary', 'bg-light');
}

async function handleNextStep() {
    if (bookingState.step === 1) {
        if (!bookingState.vehicle_id) {
            AutoPDI.toast('Please select or add a vehicle.', 'warning');
            return;
        }
    } else if (bookingState.step === 2) {
        if (!bookingState.showroom_id) {
            AutoPDI.toast('Please select a showroom location.', 'warning');
            return;
        }
    } else if (bookingState.step === 3) {
        const d = document.getElementById('wizard-date').value;
        const t = document.getElementById('wizard-time').value;
        if (!d) {
            AutoPDI.toast('Please select an inspection date.', 'warning');
            return;
        }
        bookingState.scheduled_date = d;
        bookingState.scheduled_time = t;
    } else if (bookingState.step === 4) {
        // Fetch smart recommended inspectors before transitioning to Step 5
        await loadMatchedInspectors();
    } else if (bookingState.step === 5) {
        if (!bookingState.inspector_id) {
            AutoPDI.toast('Please select a certified inspector.', 'warning');
            return;
        }
        renderBookingSummary();
    } else if (bookingState.step === 6) {
        // Submit Booking
        await submitBooking();
        return;
    }

    bookingState.step++;
    updateWizardUI();
}

function handlePrevStep() {
    if (bookingState.step > 1) {
        bookingState.step--;
        updateWizardUI();
    }
}

function updateWizardUI() {
    // Hide all step containers
    for (let i = 1; i <= 6; i++) {
        const el = document.getElementById(`wizard-step-${i}`);
        if (el) el.style.display = i === bookingState.step ? 'block' : 'none';

        const node = document.getElementById(`step-node-${i}`);
        if (node) {
            node.classList.remove('active', 'completed');
            if (i === bookingState.step) node.classList.add('active');
            else if (i < bookingState.step) node.classList.add('completed');
        }
    }

    // Toggle Back button
    const prevBtn = document.getElementById('btn-prev-step');
    if (prevBtn) prevBtn.style.display = bookingState.step === 1 ? 'none' : 'inline-flex';

    const nextBtn = document.getElementById('btn-next-step');
    if (nextBtn) {
        nextBtn.innerHTML = bookingState.step === 6 ? '<i class="bi bi-shield-check me-1"></i>Confirm & Book PDI' : 'Continue <i class="bi bi-arrow-right ms-1"></i>';
    }
}

/**
 * Smart Inspector Matching Calculation & Rendering (Step 5)
 */
async function loadMatchedInspectors() {
    const listEl = document.getElementById('wizard-inspector-list');
    if (!listEl) return;

    listEl.innerHTML = `<div class="text-center py-5"><div class="spinner-border text-primary"></div><p class="mt-2 text-muted">Calculating 6-Factor Smart Match Scores...</p></div>`;

    const url = `/api/inspectors/match?vehicle_id=${bookingState.vehicle_id}&showroom_id=${bookingState.showroom_id}&package=${bookingState.package}`;
    const res = await AutoPDI.api(url);

    if (!res.success || !res.data.length) {
        listEl.innerHTML = `<p class="text-muted text-center py-4">No verified inspectors available in this radius.</p>`;
        return;
    }

    listEl.innerHTML = res.data.map((item, idx) => {
        const insp = item.inspector;
        const b = item.breakdown;
        const isSelected = bookingState.inspector_id === insp.id || idx === 0;

        if (isSelected && !bookingState.inspector_id) {
            bookingState.inspector_id = insp.id;
            bookingState.inspector_data = insp;
            bookingState.price = item.price;
        }

        return `
            <div class="inspector-card ${isSelected ? 'border-primary' : ''} p-4 mb-3" id="insp-card-${insp.id}">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="d-flex align-items-center gap-3">
                        <img src="${insp.profile_image}" class="rounded-circle" width="56" height="56" alt="${insp.name}" style="object-fit:cover; border:2px solid var(--border-color);" onerror="this.src='/static/images/default-avatar.png'">
                        <div>
                            <h5 class="fw-bold mb-1">${insp.name}</h5>
                            <div class="d-flex align-items-center gap-2 small">
                                <span class="text-warning fw-bold"><i class="bi bi-star-fill me-1"></i>${insp.rating}</span>
                                <span class="text-muted">• ${insp.total_inspections}+ inspections</span>
                                <span class="trust-score-pill">Trust Score: ${insp.trust_score}/100</span>
                            </div>
                        </div>
                    </div>
                    <div class="text-end">
                        <span class="match-score-badge">
                            <i class="bi bi-lightning-charge-fill"></i> ${item.match_score}% Match
                        </span>
                        <div class="mt-2 fw-bold fs-5 text-primary">${AutoPDI.formatINR(item.price)}</div>
                    </div>
                </div>

                <p class="text-muted small mb-3">${insp.bio || ''}</p>

                <!-- Equipment & Certifications Badges -->
                <div class="mb-3">
                    <div class="small fw-bold text-muted mb-1">VERIFIED EQUIPMENT:</div>
                    <div class="d-flex flex-wrap gap-1">
                        ${(insp.equipment || []).map(eq => `<span class="tool-tag"><i class="bi bi-tools text-primary"></i>${eq.equipment_name}</span>`).join('')}
                    </div>
                </div>

                <!-- Match Breakdown Accordion -->
                <div class="p-2 rounded bg-light small mb-3">
                    <div class="d-flex justify-content-between text-muted" style="font-size: 0.78rem;">
                        <span>Skill: <b>${b.skill_score}%</b></span>
                        <span>Equipment: <b>${b.equipment_score}%</b></span>
                        <span>Distance (${item.distance_km}km): <b>${b.distance_score}%</b></span>
                        <span>Experience (${insp.experience_years}y): <b>${b.experience_score}%</b></span>
                    </div>
                </div>

                <div class="d-flex justify-content-end">
                    <button type="button" class="btn ${isSelected ? 'btn-pdi-primary' : 'btn-pdi-secondary'} btn-sm" 
                            onclick="selectInspector(${insp.id}, ${item.price}, ${JSON.stringify(insp).replace(/"/g, '&quot;')})">
                        ${isSelected ? '<i class="bi bi-check2-circle me-1"></i>Selected Inspector' : 'Select Inspector'}
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function selectInspector(id, price, data) {
    bookingState.inspector_id = id;
    bookingState.price = price;
    bookingState.inspector_data = data;
    document.querySelectorAll('.inspector-card').forEach(c => {
        c.classList.remove('border-primary');
        const btn = c.querySelector('button');
        if (btn) {
            btn.className = 'btn btn-pdi-secondary btn-sm';
            btn.innerHTML = 'Select Inspector';
        }
    });

    const selectedCard = document.getElementById(`insp-card-${id}`);
    if (selectedCard) {
        selectedCard.classList.add('border-primary');
        const btn = selectedCard.querySelector('button');
        if (btn) {
            btn.className = 'btn btn-pdi-primary btn-sm';
            btn.innerHTML = '<i class="bi bi-check2-circle me-1"></i>Selected Inspector';
        }
    }
}

function renderBookingSummary() {
    const summaryContainer = document.getElementById('wizard-summary-details');
    if (!summaryContainer) return;

    summaryContainer.innerHTML = `
        <div class="pdi-card mb-3">
            <h6 class="fw-bold mb-3 border-bottom pb-2">Order Review & Details</h6>
            <div class="row g-3">
                <div class="col-md-6">
                    <small class="text-muted d-block">VEHICLE</small>
                    <strong>${bookingState.vehicle_data.brand} ${bookingState.vehicle_data.model} ${bookingState.vehicle_data.variant || ''}</strong>
                    <div class="small text-muted font-monospace">VIN: ${bookingState.vehicle_data.vin}</div>
                </div>
                <div class="col-md-6">
                    <small class="text-muted d-block">SHOWROOM / DEALERSHIP</small>
                    <strong>${bookingState.showroom_data.name}</strong>
                    <div class="small text-muted">${bookingState.showroom_data.address}, ${bookingState.showroom_data.city}</div>
                </div>
                <div class="col-md-6">
                    <small class="text-muted d-block">SCHEDULED APPOINTMENT</small>
                    <strong>${bookingState.scheduled_date} at ${bookingState.scheduled_time}</strong>
                </div>
                <div class="col-md-6">
                    <small class="text-muted d-block">PDI PACKAGE</small>
                    <span class="pdi-badge pdi-badge-primary">${bookingState.package} PDI</span>
                </div>
                <div class="col-md-12">
                    <small class="text-muted d-block">ASSIGNED PDI INSPECTOR</small>
                    <strong>${bookingState.inspector_data.name}</strong> (Rating: ★ ${bookingState.inspector_data.rating} | Trust: ${bookingState.inspector_data.trust_score}/100)
                </div>
            </div>
            <hr>
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <span class="fw-bold fs-5">Total Payable Amount:</span>
                    <small class="d-block text-muted">Includes AI damage scan, dynamic checklist & tamper-proof PDF certificate</small>
                </div>
                <span class="fs-4 fw-bold text-primary">${AutoPDI.formatINR(bookingState.price)}</span>
            </div>
        </div>
    `;
}

async function submitBooking() {
    const nextBtn = document.getElementById('btn-next-step');
    nextBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Confirming Appointment...';
    nextBtn.disabled = true;

    const payload = {
        vehicle_id: bookingState.vehicle_id,
        showroom_id: bookingState.showroom_id,
        inspector_id: bookingState.inspector_id,
        inspection_type: bookingState.package,
        scheduled_date: bookingState.scheduled_date,
        scheduled_time: bookingState.scheduled_time,
        notes: document.getElementById('wizard-notes')?.value || ''
    };

    const res = await AutoPDI.api('/api/bookings', {
        method: 'POST',
        body: JSON.stringify(payload)
    });

    if (res.success) {
        AutoPDI.toast('PDI Appointment booked successfully!', 'success');
        setTimeout(() => {
            window.location.href = '/customer/dashboard';
        }, 800);
    } else {
        nextBtn.innerHTML = '<i class="bi bi-shield-check me-1"></i>Confirm & Book PDI';
        nextBtn.disabled = false;
    }
}

/**
 * Load Vehicles Page
 */
async function loadVehiclesPage() {
    const res = await AutoPDI.api('/api/vehicles');
    const container = document.getElementById('vehicles-page-list');
    if (!container || !res.success) return;

    if (res.data.length === 0) {
        container.innerHTML = `<div class="col-12 text-center py-5 text-muted">No vehicles registered yet.</div>`;
        return;
    }

    container.innerHTML = res.data.map(v => `
        <div class="col-md-6 mb-4">
            <div class="pdi-card pdi-card-hover p-4">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <span class="pdi-badge pdi-badge-primary mb-2">${v.vehicle_type} • ${v.fuel_type}</span>
                        <h4 class="fw-bold mb-1">${v.brand} ${v.model}</h4>
                        <p class="text-muted small mb-2">${v.variant || ''}</p>
                    </div>
                    <button class="btn btn-outline-danger btn-sm" onclick="deleteVehicle(${v.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
                <div class="bg-light p-2 rounded small text-muted font-monospace mb-3">
                    VIN: <b>${v.vin.startsWith('PENDING-') ? 'Pending Dealer Allotment' : v.vin}</b><br>
                    Reg: ${v.registration_number || 'Applied / Unregistered'}
                </div>
                <a href="/customer/book" class="btn btn-pdi-primary btn-sm w-100">
                    <i class="bi bi-calendar-plus me-1"></i>Book PDI for this vehicle
                </a>
            </div>
        </div>
    `).join('');
}

async function deleteVehicle(id) {
    if (!confirm('Are you sure you want to remove this vehicle?')) return;
    const res = await AutoPDI.api(`/api/vehicles/${id}`, { method: 'DELETE' });
    if (res.success) {
        AutoPDI.toast('Vehicle removed.', 'success');
        loadVehiclesPage();
    }
}
