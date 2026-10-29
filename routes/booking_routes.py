from datetime import datetime, time
from flask import Blueprint, request, session
from models import db
from models.user import User
from models.vehicle import Vehicle
from models.showroom import Showroom
from models.inspector import Inspector
from models.booking import Booking
from models.inspection import Inspection
from services.matching_service import rank_inspectors_for_booking
from services.notification_service import create_notification, notify_admin
from utils.auth import login_required, role_required, get_current_user
from utils.helpers import success_response, error_response, generate_verification_code

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/api/showrooms', methods=['GET', 'POST'])
@login_required
def api_showrooms():
    if request.method == 'GET':
        showrooms = Showroom.query.order_by(Showroom.name.asc()).all()
        return success_response("Showrooms list", data=[s.to_dict() for s in showrooms])

    # POST create showroom if not existing
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    address = data.get('address', '').strip()
    city = data.get('city', 'Bangalore').strip()
    lat = float(data.get('latitude', 12.9716))
    lon = float(data.get('longitude', 77.5946))
    contact = data.get('contact_number', '')

    if not name or not address:
        return error_response("Showroom name and address are required.", 400)

    showroom = Showroom(
        name=name,
        address=address,
        city=city,
        latitude=lat,
        longitude=lon,
        contact_number=contact
    )
    db.session.add(showroom)
    db.session.commit()
    return success_response("Showroom added", data=showroom.to_dict(), status_code=201)


@booking_bp.route('/api/inspectors/match', methods=['GET'])
@login_required
def api_match_inspectors():
    vehicle_id = request.args.get('vehicle_id', type=int)
    showroom_id = request.args.get('showroom_id', type=int)
    package = request.args.get('package', 'PREMIUM').upper()

    vehicle = Vehicle.query.get(vehicle_id) if vehicle_id else None
    showroom = Showroom.query.get(showroom_id) if showroom_id else None

    if not vehicle or not showroom:
        # Fallback dummy vehicle and showroom for matching calculation if not selected yet
        vehicle = vehicle or Vehicle(brand='Hyundai', model='Creta', vehicle_type='ICE')
        showroom = showroom or Showroom(name='City Showroom', latitude=12.9716, longitude=77.5946)

    ranked_inspectors = rank_inspectors_for_booking(vehicle, showroom, package)
    return success_response("Recommended inspectors", data=ranked_inspectors)


@booking_bp.route('/api/bookings', methods=['GET', 'POST'])
@login_required
def api_bookings():
    user = get_current_user()

    if request.method == 'GET':
        if user.role == 'CUSTOMER':
            bookings = Booking.query.filter_by(customer_id=user.id).order_by(Booking.created_at.desc()).all()
        elif user.role == 'INSPECTOR':
            inspector = user.inspector_profile
            if not inspector:
                return success_response("No bookings", data=[])
            bookings = Booking.query.filter_by(inspector_id=inspector.id).order_by(Booking.created_at.desc()).all()
        else:  # ADMIN
            bookings = Booking.query.order_by(Booking.created_at.desc()).all()

        return success_response("Bookings list", data=[b.to_dict() for b in bookings])

    # POST Create new booking
    data = request.get_json() or {}
    vehicle_id = data.get('vehicle_id')
    showroom_id = data.get('showroom_id')
    inspector_id = data.get('inspector_id')
    package = data.get('inspection_type', 'PREMIUM').upper()
    scheduled_date_str = data.get('scheduled_date')
    scheduled_time_str = data.get('scheduled_time', '10:00')
    notes = data.get('notes', '')

    if not vehicle_id or not showroom_id or not scheduled_date_str:
        return error_response("Vehicle, Showroom, and Scheduled Date are required.", 400)

    try:
        scheduled_date = datetime.strptime(scheduled_date_str, '%Y-%m-%d').date()
        scheduled_time = datetime.strptime(scheduled_time_str, '%H:%M').time()
    except ValueError:
        return error_response("Invalid date or time format.", 400)

    inspector = Inspector.query.get(inspector_id) if inspector_id else None
    price = 2499.00 if package == 'PREMIUM' else 1499.00
    if inspector:
        price = inspector.price_premium if package == 'PREMIUM' else inspector.price_standard

    booking = Booking(
        customer_id=user.id,
        vehicle_id=vehicle_id,
        showroom_id=showroom_id,
        inspector_id=inspector.id if inspector else None,
        inspection_type=package,
        scheduled_date=scheduled_date,
        scheduled_time=scheduled_time,
        price=price,
        status='REQUESTED',
        payment_status='PAID',  # Mock successful checkout
        notes=notes
    )
    db.session.add(booking)
    db.session.commit()

    # Notify Inspector
    if inspector and inspector.user_id:
        create_notification(
            user_id=inspector.user_id,
            booking_id=booking.id,
            title="New PDI Inspection Request",
            message=f"You have a new {package} PDI booking request for {booking.vehicle.brand} {booking.vehicle.model}.",
            notif_type='INFO'
        )

    # Notify Admin
    notify_admin(
        title="New PDI Booking Created",
        message=f"Booking #{booking.id} created for {booking.vehicle.brand} {booking.vehicle.model} by {user.name}.",
        booking_id=booking.id
    )

    return success_response("PDI Inspection booked successfully!", data=booking.to_dict(), status_code=201)


@booking_bp.route('/api/bookings/<int:booking_id>', methods=['GET'])
@login_required
def api_booking_detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return success_response("Booking details", data=booking.to_dict())


@booking_bp.route('/api/bookings/<int:booking_id>/accept', methods=['POST'])
@role_required('INSPECTOR')
def api_accept_booking(booking_id):
    user = get_current_user()
    inspector = user.inspector_profile
    booking = Booking.query.get_or_404(booking_id)

    if booking.inspector_id != inspector.id:
        return error_response("You are not assigned to this booking.", 403)

    booking.status = 'ACCEPTED'

    # Create Inspection Record if not already created
    if not booking.inspection:
        verification_code = generate_verification_code()
        inspection = Inspection(
            booking_id=booking.id,
            vehicle_id=booking.vehicle_id,
            inspector_id=inspector.id,
            verification_code=verification_code,
            final_status='ATTENTION_REQUIRED'
        )
        db.session.add(inspection)
    
    db.session.commit()

    # Notify Customer
    create_notification(
        user_id=booking.customer_id,
        booking_id=booking.id,
        title="Inspector Accepted Your Booking",
        message=f"{user.name} has accepted your PDI booking for {booking.scheduled_date.strftime('%d %b %Y')}.",
        notif_type='SUCCESS'
    )

    return success_response("Booking accepted. Inspection workspace initialized.", data=booking.to_dict())


@booking_bp.route('/api/bookings/<int:booking_id>/reject', methods=['POST'])
@role_required('INSPECTOR')
def api_reject_booking(booking_id):
    user = get_current_user()
    inspector = user.inspector_profile
    booking = Booking.query.get_or_404(booking_id)

    if booking.inspector_id != inspector.id:
        return error_response("You are not assigned to this booking.", 403)

    booking.status = 'REJECTED'
    db.session.commit()

    create_notification(
        user_id=booking.customer_id,
        booking_id=booking.id,
        title="Inspection Request Declined",
        message=f"Inspector {user.name} was unavailable for your scheduled time. Please select another inspector.",
        notif_type='WARNING'
    )

    return success_response("Booking rejected.", data=booking.to_dict())


@booking_bp.route('/api/bookings/<int:booking_id>/cancel', methods=['PUT'])
@login_required
def api_cancel_booking(booking_id):
    user = get_current_user()
    booking = Booking.query.get_or_404(booking_id)

    if user.role == 'CUSTOMER' and booking.customer_id != user.id:
        return error_response("Unauthorized", 403)

    booking.status = 'CANCELLED'
    db.session.commit()

    return success_response("Booking cancelled successfully.", data=booking.to_dict())
