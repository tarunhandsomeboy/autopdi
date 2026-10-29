from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session
from models import db
from models.user import User
from models.vehicle import Vehicle
from models.booking import Booking
from models.inspection import Inspection
from models.report import Report
from models.issue import IssueResolution
from utils.auth import login_required, role_required, get_current_user
from utils.helpers import success_response, error_response
from utils.validators import validate_vin

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customer/dashboard')
@role_required('CUSTOMER')
def dashboard():
    user = get_current_user()
    return render_template('customer/dashboard.html', user=user)


@customer_bp.route('/customer/book')
@role_required('CUSTOMER')
def book_pdi():
    user = get_current_user()
    return render_template('customer/book_pdi.html', user=user)


@customer_bp.route('/customer/vehicles')
@role_required('CUSTOMER')
def vehicles_page():
    user = get_current_user()
    return render_template('customer/vehicles.html', user=user)


@customer_bp.route('/customer/bookings')
@role_required('CUSTOMER')
def bookings_page():
    user = get_current_user()
    return render_template('customer/bookings.html', user=user)


@customer_bp.route('/customer/report/<int:inspection_id>')
@role_required('CUSTOMER', 'INSPECTOR', 'ADMIN')
def view_report(inspection_id):
    user = get_current_user()
    inspection = Inspection.query.get_or_404(inspection_id)
    return render_template('customer/report_view.html', user=user, inspection=inspection)


@customer_bp.route('/customer/issues')
@role_required('CUSTOMER')
def issues_page():
    user = get_current_user()
    return render_template('customer/issues.html', user=user)


# --- REST API Endpoints ---

@customer_bp.route('/api/customer/dashboard', methods=['GET'])
@role_required('CUSTOMER')
def api_dashboard_stats():
    user = get_current_user()
    bookings = Booking.query.filter_by(customer_id=user.id).order_by(Booking.created_at.desc()).all()
    vehicles = Vehicle.query.filter_by(customer_id=user.id).all()

    upcoming = [b.to_dict() for b in bookings if b.status in ['REQUESTED', 'ACCEPTED', 'IN_PROGRESS']]
    completed = [b.to_dict() for b in bookings if b.status == 'COMPLETED']
    
    # Reports
    completed_inspections = (
        Inspection.query.join(Booking)
        .filter(Booking.customer_id == user.id, Inspection.completed_at.isnot(None))
        .order_by(Inspection.completed_at.desc())
        .all()
    )

    return success_response("Customer dashboard data", data={
        "stats": {
            "total_vehicles": len(vehicles),
            "upcoming_pdi_count": len(upcoming),
            "completed_pdi_count": len(completed),
            "reports_count": len(completed_inspections)
        },
        "upcoming_bookings": upcoming[:5],
        "completed_bookings": completed[:5],
        "vehicles": [v.to_dict() for v in vehicles],
        "reports": [
            {
                "inspection_id": insp.id,
                "verification_code": insp.verification_code,
                "vehicle_name": f"{insp.vehicle.brand} {insp.vehicle.model}",
                "overall_score": insp.overall_score,
                "final_status": insp.final_status,
                "date": insp.completed_at.strftime('%d %b %Y') if insp.completed_at else ''
            } for insp in completed_inspections[:5]
        ]
    })


@customer_bp.route('/api/vehicles', methods=['GET', 'POST'])
@role_required('CUSTOMER')
def api_vehicles():
    user = get_current_user()

    if request.method == 'GET':
        vehicles = Vehicle.query.filter_by(customer_id=user.id).order_by(Vehicle.created_at.desc()).all()
        return success_response("Vehicles retrieved", data=[v.to_dict() for v in vehicles])

    # POST new vehicle
    data = request.get_json() or {}
    brand = data.get('brand', '').strip()
    model = data.get('model', '').strip()
    variant = data.get('variant', '').strip()
    fuel_type = data.get('fuel_type', 'Petrol')
    vehicle_type = data.get('vehicle_type', 'ICE').upper()
    vin = data.get('vin', '').strip().upper()
    reg_no = data.get('registration_number', '').strip().upper()
    mfg_date_str = data.get('manufacturing_date', '')

    if not brand or not model:
        return error_response("Brand and Model are required.", 400)

    if vin:
        if not validate_vin(vin):
            return error_response("Please enter a valid VIN (5 to 17 alphanumeric characters).", 400)
    else:
        import uuid
        vin = f"PENDING-{uuid.uuid4().hex[:8].upper()}"

    mfg_date = None
    if mfg_date_str:
        try:
            mfg_date = datetime.strptime(mfg_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    vehicle = Vehicle(
        customer_id=user.id,
        brand=brand,
        model=model,
        variant=variant,
        fuel_type=fuel_type,
        vehicle_type=vehicle_type,
        vin=vin,
        registration_number=reg_no or None,
        manufacturing_date=mfg_date
    )
    db.session.add(vehicle)
    db.session.commit()

    return success_response("Vehicle added successfully", data=vehicle.to_dict(), status_code=201)


@customer_bp.route('/api/vehicles/<int:vehicle_id>', methods=['GET', 'DELETE'])
@role_required('CUSTOMER')
def api_vehicle_detail(vehicle_id):
    user = get_current_user()
    vehicle = Vehicle.query.filter_by(id=vehicle_id, customer_id=user.id).first()
    if not vehicle:
        return error_response("Vehicle not found", 404)

    if request.method == 'GET':
        return success_response("Vehicle details", data=vehicle.to_dict())

    # DELETE
    db.session.delete(vehicle)
    db.session.commit()
    return success_response("Vehicle deleted successfully")
