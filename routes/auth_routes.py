from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from models import db
from models.user import User
from models.inspector import Inspector
from utils.auth import login_user, logout_user, login_required, get_current_user
from utils.validators import validate_email, validate_phone, validate_password_strength
from utils.helpers import success_response, error_response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    if 'user_id' in session:
        role = session.get('user_role')
        if role == 'CUSTOMER':
            return redirect(url_for('customer.dashboard'))
        elif role == 'INSPECTOR':
            return redirect(url_for('inspector.dashboard'))
        elif role == 'ADMIN':
            return redirect(url_for('admin.dashboard'))
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET'])
def register():
    if 'user_id' in session:
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# --- REST API Endpoints ---

@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return error_response("Email and password are required.", 400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error_response("Invalid email or password.", 401)

    if user.status == 'BLOCKED':
        return error_response("Your account has been suspended. Please contact support.", 403)

    login_user(user)

    redirect_url = '/customer/dashboard'
    if user.role == 'INSPECTOR':
        redirect_url = '/inspector/dashboard'
    elif user.role == 'ADMIN':
        redirect_url = '/admin/dashboard'

    return success_response(
        f"Welcome back, {user.name}!",
        data={
            "user": user.to_dict(),
            "redirect_url": redirect_url
        }
    )


@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'CUSTOMER').upper()

    if role not in ['CUSTOMER', 'INSPECTOR']:
        role = 'CUSTOMER'

    if not name:
        return error_response("Full Name is required.", 400)
    if not validate_email(email):
        return error_response("Please enter a valid email address.", 400)
    if not validate_phone(phone):
        return error_response("Please enter a valid phone number.", 400)
    
    is_valid_pw, pw_msg = validate_password_strength(password)
    if not is_valid_pw:
        return error_response(pw_msg, 400)

    if User.query.filter_by(email=email).first():
        return error_response("An account with this email already exists.", 409)

    # Create User
    user = User(
        name=name,
        email=email,
        phone=phone,
        role=role,
        status='ACTIVE' if role == 'CUSTOMER' else 'PENDING'
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    # If inspector, create inspector profile
    if role == 'INSPECTOR':
        experience_years = int(data.get('experience_years', 1))
        bio = data.get('bio', 'Certified automotive pre-delivery inspection specialist.')
        specialization = data.get('specialization', 'ICE, EV, Hybrid')
        
        inspector = Inspector(
            user_id=user.id,
            bio=bio,
            experience_years=experience_years,
            specialization=specialization,
            verification_status='PENDING',
            availability_status='AVAILABLE',
            rating=5.0,
            trust_score=85
        )
        db.session.add(inspector)

    db.session.commit()
    login_user(user)

    redirect_url = '/customer/dashboard' if role == 'CUSTOMER' else '/inspector/dashboard'

    return success_response(
        "Registration successful!",
        data={
            "user": user.to_dict(),
            "redirect_url": redirect_url
        },
        status_code=201
    )


@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def api_me():
    user = get_current_user()
    if not user:
        return error_response("User not found", 404)
    return success_response("User details retrieved", data={"user": user.to_dict(include_sensitive=True)})
