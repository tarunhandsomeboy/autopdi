from datetime import datetime, date
from flask import Blueprint, render_template, request, session
from models import db
from models.user import User
from models.inspector import Inspector, InspectorSpecialization
from models.equipment import Equipment
from models.certification import Certification
from models.booking import Booking
from models.inspection import Inspection
from utils.auth import role_required, get_current_user
from utils.helpers import success_response, error_response

inspector_bp = Blueprint('inspector', __name__)

@inspector_bp.route('/inspector/dashboard')
@role_required('INSPECTOR')
def dashboard():
    user = get_current_user()
    return render_template('inspector/dashboard.html', user=user)


@inspector_bp.route('/inspector/requests')
@role_required('INSPECTOR')
def requests_page():
    user = get_current_user()
    return render_template('inspector/requests.html', user=user)


@inspector_bp.route('/inspector/profile')
@role_required('INSPECTOR')
def profile_page():
    user = get_current_user()
    return render_template('inspector/profile.html', user=user)


# --- REST API Endpoints ---

@inspector_bp.route('/api/inspector/dashboard', methods=['GET'])
@role_required('INSPECTOR')
def api_dashboard_stats():
    user = get_current_user()
    inspector = user.inspector_profile
    if not inspector:
        return error_response("Inspector profile not found", 404)

    today = date.today()
    bookings = Booking.query.filter_by(inspector_id=inspector.id).all()

    today_count = sum(1 for b in bookings if b.scheduled_date == today and b.status in ['ACCEPTED', 'IN_PROGRESS'])
    pending_count = sum(1 for b in bookings if b.status == 'REQUESTED')
    completed_count = sum(1 for b in bookings if b.status == 'COMPLETED')
    
    # Calculate demo earnings
    total_earnings = sum(b.price for b in bookings if b.status == 'COMPLETED')

    # Pending requests
    pending_requests = [
        b.to_dict() for b in bookings if b.status == 'REQUESTED'
    ]

    # Active inspections
    active_inspections = (
        Inspection.query.filter_by(inspector_id=inspector.id, completed_at=None)
        .order_by(Inspection.created_at.desc())
        .all()
    )

    return success_response("Inspector dashboard stats", data={
        "stats": {
            "today_inspections": today_count,
            "pending_requests": pending_count,
            "completed_inspections": completed_count,
            "rating": round(inspector.rating, 2),
            "trust_score": inspector.trust_score,
            "earnings": total_earnings,
            "verification_status": inspector.verification_status,
            "availability_status": inspector.availability_status
        },
        "pending_requests": pending_requests,
        "active_inspections": [insp.to_dict() for insp in active_inspections],
        "profile": inspector.to_dict(include_details=True)
    })


@inspector_bp.route('/api/inspector/equipment', methods=['POST'])
@role_required('INSPECTOR')
def api_add_equipment():
    user = get_current_user()
    inspector = user.inspector_profile
    data = request.get_json() or {}
    
    eq_name = data.get('equipment_name', '').strip()
    eq_type = data.get('equipment_type', 'DIAGNOSTIC')
    serial = data.get('serial_number', '').strip()

    if not eq_name:
        return error_response("Equipment name is required.", 400)

    eq = Equipment(
        inspector_id=inspector.id,
        equipment_name=eq_name,
        equipment_type=eq_type,
        serial_number=serial or None,
        verification_status='PENDING'  # Admin will verify
    )
    db.session.add(eq)
    db.session.commit()

    return success_response("Equipment registered. Pending admin verification.", data=eq.to_dict(), status_code=201)


@inspector_bp.route('/api/inspector/certifications', methods=['POST'])
@role_required('INSPECTOR')
def api_add_certification():
    user = get_current_user()
    inspector = user.inspector_profile
    data = request.get_json() or {}

    cert_name = data.get('certificate_name', '').strip()
    issuer = data.get('issuer', '').strip()
    cert_num = data.get('certificate_number', '').strip()

    if not cert_name or not issuer:
        return error_response("Certificate name and Issuer are required.", 400)

    cert = Certification(
        inspector_id=inspector.id,
        certificate_name=cert_name,
        issuer=issuer,
        certificate_number=cert_num or None,
        verification_status='PENDING'
    )
    db.session.add(cert)
    db.session.commit()

    return success_response("Certification registered. Pending admin verification.", data=cert.to_dict(), status_code=201)


@inspector_bp.route('/api/inspector/profile', methods=['PUT'])
@role_required('INSPECTOR')
def api_update_profile():
    user = get_current_user()
    inspector = user.inspector_profile
    data = request.get_json() or {}

    if 'bio' in data:
        inspector.bio = data['bio']
    if 'availability_status' in data:
        inspector.availability_status = data['availability_status'].upper()
    if 'experience_years' in data:
        inspector.experience_years = int(data['experience_years'])
    if 'specialization' in data:
        inspector.specialization = data['specialization']
    if 'price_standard' in data:
        inspector.price_standard = float(data['price_standard'])
    if 'price_premium' in data:
        inspector.price_premium = float(data['price_premium'])
    if 'phone' in data:
        user.phone = data['phone']

    db.session.commit()
    return success_response("Profile updated successfully", data=inspector.to_dict(include_details=True))
