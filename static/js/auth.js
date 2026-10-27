/**
 * AUTO PDI — Authentication Handlers
 */

document.addEventListener('DOMContentLoaded', () => {
    // Login Form Handler
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = loginForm.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Logging in...';
            btn.disabled = true;

            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;

            const res = await AutoPDI.api('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });

            if (res.success) {
                AutoPDI.toast(res.message || 'Login successful!', 'success');
                setTimeout(() => {
                    window.location.href = res.data.redirect_url || '/customer/dashboard';
                }, 500);
            } else {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
    }

    // Register Form Handler
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        const roleSelect = document.getElementById('role');
        const inspectorFields = document.getElementById('inspector-extra-fields');

        if (roleSelect && inspectorFields) {
            roleSelect.addEventListener('change', () => {
                if (roleSelect.value === 'INSPECTOR') {
                    inspectorFields.style.display = 'block';
                } else {
                    inspectorFields.style.display = 'none';
                }
            });
        }

        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = registerForm.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Registering...';
            btn.disabled = true;

            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const password = document.getElementById('password').value;
            const role = roleSelect ? roleSelect.value : 'CUSTOMER';

            const payload = { name, email, phone, password, role };
            if (role === 'INSPECTOR') {
                payload.experience_years = document.getElementById('experience_years')?.value || 1;
                payload.specialization = document.getElementById('specialization')?.value || 'ICE, EV, Hybrid';
                payload.bio = document.getElementById('bio')?.value || '';
            }

            const res = await AutoPDI.api('/api/auth/register', {
                method: 'POST',
                body: JSON.stringify(payload)
            });

            if (res.success) {
                AutoPDI.toast('Account registered successfully! Redirecting...', 'success');
                setTimeout(() => {
                    window.location.href = res.data.redirect_url || '/customer/dashboard';
                }, 600);
            } else {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
    }
});
