import pytest
from datetime import date, time
from app import create_app
from models import db
from models.user import User
from models.vehicle import Vehicle
from models.showroom import Showroom
from models.inspector import Inspector
from models.booking import Booking
from models.inspection import Inspection
from services.scoring_service import calculate_inspection_readiness_score
from routes.inspection_routes import generate_checkpoints_for_inspection

@pytest.fixture
def app_ctx():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

def test_inspection_checkpoints_and_readiness_score(app_ctx):
    cust = User(name="Buyer", email="buyer@test.com", role="CUSTOMER")
    cust.set_password("Password@123")
    insp_u = User(name="Inspector", email="insp@test.com", role="INSPECTOR")
    insp_u.set_password("Password@123")
    db.session.add_all([cust, insp_u])
    db.session.flush()

    insp = Inspector(user_id=insp_u.id, verification_status="VERIFIED")
    show = Showroom(name="Auto Mall", address="Indiranagar", city="Bangalore")
    veh = Vehicle(customer_id=cust.id, brand="Tata", model="Nexon EV", vehicle_type="EV", vin="TATANEXON12345")
    db.session.add_all([insp, show, veh])
    db.session.flush()

    booking = Booking(
        customer_id=cust.id,
        vehicle_id=veh.id,
        showroom_id=show.id,
        inspector_id=insp.id,
        inspection_type="PREMIUM",
        scheduled_date=date.today(),
        scheduled_time=time(10, 0),
        status="IN_PROGRESS"
    )
    db.session.add(booking)
    db.session.flush()

    inspection = Inspection(
        booking_id=booking.id,
        vehicle_id=veh.id,
        inspector_id=insp.id,
        vin_verified=True,
        verification_code="PDI-2026-TEST1"
    )
    db.session.add(inspection)
    db.session.commit()

    # Generate dynamic checkpoints for EV
    generate_checkpoints_for_inspection(inspection)
    assert inspection.checkpoints.count() > 20

    # Calculate initial score (all PASS -> 100%)
    score_data = calculate_inspection_readiness_score(inspection)
    assert score_data['overall_score'] == 100.0
    assert score_data['final_status'] == 'DELIVERY_READY'

    # Set some items to ATTENTION and FAIL
    cps = inspection.checkpoints.all()
    cps[0].status = 'ATTENTION'
    cps[1].status = 'FAIL'
    db.session.commit()

    score_data_updated = calculate_inspection_readiness_score(inspection)
    assert score_data_updated['overall_score'] < 100.0
