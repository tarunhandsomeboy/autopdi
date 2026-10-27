/**
 * AUTO PDI — Master JavaScript Utilities
 * Fetch API helpers, Toast Notifications, Offline Monitoring & Modals
 */

const AutoPDI = {
    // API Helper with JSON parsing & error handling
    async api(endpoint, options = {}) {
        const defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        const isFormData = options.body instanceof FormData;
        if (isFormData) {
            delete defaultHeaders['Content-Type'];
        }

        const config = {
            ...options,
            headers: isFormData ? options.headers || {} : { ...defaultHeaders, ...options.headers }
        };

        try {
            const response = await fetch(endpoint, config);
            const data = await response.json().catch(() => ({ success: false, message: 'Invalid server response' }));

            if (!response.ok) {
                const errorMsg = data.message || `Request failed with status ${response.status}`;
                this.toast(errorMsg, 'danger');
                return { success: false, error: errorMsg, status: response.status, data };
            }

            return data;
        } catch (err) {
            console.error(`API Error [${endpoint}]:`, err);
            this.toast('Network error or server unreachable. Please try again.', 'danger');
            return { success: false, error: err.message };
        }
    },

    // Toast Notification System
    toast(message, type = 'info', duration = 4000) {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `pdi-toast toast-${type}`;

        let icon = 'bi-info-circle-fill text-primary';
        if (type === 'success') icon = 'bi-check-circle-fill text-success';
        if (type === 'warning') icon = 'bi-exclamation-triangle-fill text-warning';
        if (type === 'danger') icon = 'bi-x-circle-fill text-danger';

        toast.innerHTML = `
            <i class="bi ${icon} fs-5"></i>
            <div style="flex: 1; font-size: 0.88rem; font-weight: 500;">
                ${message}
            </div>
            <button type="button" style="background:none; border:none; color:#94A3B8; cursor:pointer;" onclick="this.parentElement.remove()">
                <i class="bi bi-x fs-6"></i>
            </button>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.transition = 'all 0.3s ease';
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(100%)';
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    },

    // Geolocation Helper
    async getGeolocation() {
        return new Promise((resolve) => {
            if (!navigator.geolocation) {
                resolve({ latitude: null, longitude: null });
                return;
            }
            navigator.geolocation.getCurrentPosition(
                (pos) => resolve({
                    latitude: roundNumber(pos.coords.latitude, 6),
                    longitude: roundNumber(pos.coords.longitude, 6)
                }),
                (err) => {
                    console.warn('Geolocation access declined or unavailable:', err.message);
                    resolve({ latitude: null, longitude: null });
                },
                { timeout: 6000, enableHighAccuracy: true }
            );
        });
    },

    // Format Currency
    formatINR(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount);
    }
};

function roundNumber(num, decimals = 2) {
    return Number(Math.round(num + 'e' + decimals) + 'e-' + decimals);
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
    // Monitor online/offline state
    window.addEventListener('online', () => AutoPDI.toast('Network connected. System is online.', 'success'));
    window.addEventListener('offline', () => AutoPDI.toast('Offline mode active. Checkpoint drafts saved locally.', 'warning'));
});
