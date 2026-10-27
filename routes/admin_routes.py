from datetime import datetime
from flask import Blueprint, render_template, request
from models import db
from models.user import User
from models.inspector import Inspector
from models.vehicle import Vehicle
from models.booking import Booking
from models.inspection import Inspection
from models.equipment import Equipment
from models.certification import Certification
from models.report import Report
from services.notification_service import create_notification
from services.scoring_service import calculate_inspector_trust_score
from utils.auth import role_required, get_current_user
from utils.helpers import success_response, error_response

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@role_required('ADMIN')
def dashboard():
    user = get_current_user()
    return render_template('admin/dashboard.html', user=user)


@admin_bp.route('/admin/inspectors')
@role_required('ADMIN')
def inspectors_page():
    user = get_current_user()
    return render_template('admin/inspectors.html', user=user)


@admin_bp.route('/admin/customers')
@role_required('ADMIN')
def customers_page():
    user = get_current_user()
    return render_template('admin/customers.html', user=user)


@admin_bp.route('/admin/bookings')
@role_required('ADMIN')
def bookings_page():
    user = get_current_user()
    return render_template('admin/bookings.html', user=user)


@admin_bp.route('/admin/reports')
@role_required('ADMIN')
def reports_page():
    user = get_current_user()
    return render_template('admin/reports.html', user=user)


# --- REST API Endpoints ---

@admin_bp.route('/api/admin/dashboard', methods=['GET'])
@role_required('ADMIN')
def api_dashboard_stats():
    total_customers = User.query.filter_by(role='CUSTOMER').count()
    total_inspectors = Inspector.query.count()
    verified_inspectors = Inspector.query.filter_by(verification_status='VERIFIED').count()
    pending_inspectors = Inspector.query.filter_by(verification_status='PENDING').count()
    total_bookings = Booking.query.count()
    active_inspections = Booking.query.filter_by(status='IN_PROGRESS').count()
    completed_inspections = Booking.query.filter_by(status='COMPLETED').count()
    
    # Revenue & Ratings
    all_completed = Booking.query.filter_by(status='COMPLETED').all()
    total_revenue = sum(b.price for b in all_completed)
    
    inspectors = Inspector.query.all()
    avg_rating = round(sum(i.rating for i in inspectors) / len(inspectors), 2) if inspectors else 5.0

    # Chart 1: Bookings by Status
    status_counts = {
        'Requested': Booking.query.filter_by(status='REQUESTED').count(),
        'Accepted': Booking.query.filter_by(status='ACCEPTED').count(),
        'In Progress': Booking.query.filter_by(status='IN_PROGRESS').count(),
        'Completed': Booking.query.filter_by(status='COMPLETED').count(),
        'Cancelled': Booking.query.filter_by(status='CANCELLED').count()
    }

    # Chart 2: Vehicle Type Distribution
    v_types = {
        'ICE (Petrol/Diesel)': Vehicle.query.filter_by(vehicle_type='ICE').count(),
        'EV (Electric)': Vehicle.query.filter_by(vehicle_type='EV').count(),
        'Hybrid': Vehicle.query.filter_by(vehicle_type='HYBRID').count()
    }

    # Chart 3: Standard vs Premium
    packages = {
        'Standard PDI': Booking.query.filter_by(inspection_type='STANDARD').count(),
        'Premium PDI': Booking.query.filter_by(inspection_type='PREMIUM').count()
    }

    # Chart 4: Readiness Verdict Distribution
    verdicts = {
        'Delivery Ready (>=90)': Inspection.query.filter_by(final_status='DELIVERY_READY').count(),
        'Attention Required (75-89)': Inspection.query.filter_by(final_status='ATTENTION_REQUIRED').count(),
        'Hold Delivery (<75)': Inspection.query.filter_by(final_status='HOLD_DELIVERY').count()
    }

    # Top Inspectors
    top_inspectors = [
        {
            'name': i.user.name if i.user else 'Inspector',
            'rating': round(i.rating, 1),
            'inspections': i.total_inspections,
            'trust_score': i.trust_score
        }
        for i in sorted(inspectors, key=lambda x: (x.total_inspections, x.rating), reverse=True)[:5]
    ]

    return success_response("Admin analytics data", data={
        "kpis": {
            "total_customers": total_customers,
            "total_inspectors": total_inspectors,
            "verified_inspectors": verified_inspectors,
            "pending_inspectors": pending_inspectors,
            "total_bookings": total_bookings,
            "active_inspections": active_inspections,
            "completed_inspections": completed_inspections,
            "avg_rating": avg_rating,
            "total_revenue": total_revenue
        },
        "charts": {
            "booking_status": status_counts,
            "vehicle_types": v_types,
            "packages": packages,
            "verdicts": verdicts,
            "monthly_trend": {
                "labels": ["Mar", "Apr", "May", "Jun", "Jul", "Aug"],
                "bookings": [12, 19, 28, 42, 65, total_bookings or 89]
            }
        },
        "top_inspectors": top_inspectors
    })


@admin_bp.route('/api/admin/inspectors', methods=['GET'])
@role_required('ADMIN')
def api_list_inspectors():
    inspectors = Inspector.query.order_by(Inspector.created_at.desc()).all()
    return success_response("Inspectors list", data=[i.to_dict(include_details=True) for i in inspectors])


@admin_bp.route('/api/admin/inspectors/<int:inspector_id>/approve', methods=['PUT'])
@role_required('ADMIN')
def api_approve_inspector(inspector_id):
    inspector = Inspector.query.get_or_404(inspector_id)
    inspector.verification_status = 'VERIFIED'
    if inspector.user:
        inspector.user.status = 'ACTIVE'
    inspector.trust_score = calculate_inspector_trust_score(inspector)
    db.session.commit()

    if inspector.user:
        create_notification(
            user_id=inspector.user.id,
            title="Inspector Application Approved ✓",
            message="Congratulations! Your Auto PDI inspector credentials have been approved.",
            notif_type='SUCCESS'
        )

    return success_response("Inspector approved successfully", data=inspector.to_dict(include_details=True))


@admin_bp.route('/api/admin/inspectors/<int:inspector_id>/reject', methods=['PUT'])
@role_required('ADMIN')
def api_reject_inspector(inspector_id):
    inspector = Inspector.query.get_or_404(inspector_id)
    inspector.verification_status = 'REJECTED'
    db.session.commit()

    if inspector.user:
        create_notification(
            user_id=inspector.user.id,
            title="Inspector Application Status",
            message="Your inspector application was not approved. Please contact support.",
            notif_type='WARNING'
        )

    return success_response("Inspector rejected", data=inspector.to_dict())


@admin_bp.route('/api/admin/inspectors/<int:inspector_id>/suspend', methods=['PUT'])
@role_required('ADMIN')
def api_suspend_inspector(inspector_id):
    inspector = Inspector.query.get_or_404(inspector_id)
    inspector.verification_status = 'SUSPENDED'
    if inspector.user:
        inspector.user.status = 'BLOCKED'
    db.session.commit()
    return success_response("Inspector suspended", data=inspector.to_dict())


@admin_bp.route('/api/admin/equipment/<int:equipment_id>/verify', methods=['PUT'])
@role_required('ADMIN')
def api_verify_equipment(equipment_id):
    eq = Equipment.query.get_or_404(equipment_id)
    eq.verification_status = 'VERIFIED'
    eq.inspector.trust_score = calculate_inspector_trust_score(eq.inspector)
    db.session.commit()
    return success_response(f"Equipment '{eq.equipment_name}' verified ✓", data=eq.to_dict())


@admin_bp.route('/api/admin/certifications/<int:cert_id>/verify', methods=['PUT'])
@role_required('ADMIN')
def api_verify_certification(cert_id):
    cert = Certification.query.get_or_404(cert_id)
    cert.verification_status = 'VERIFIED'
    cert.inspector.trust_score = calculate_inspector_trust_score(cert.inspector)
    db.session.commit()
    return success_response(f"Certification '{cert.certificate_name}' verified ✓", data=cert.to_dict())


@admin_bp.route('/api/admin/users', methods=['GET'])
@role_required('ADMIN')
def api_list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return success_response("Users list", data=[u.to_dict() for u in users])
