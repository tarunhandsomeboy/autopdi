import pytest
from datetime import date, time
from app import create_app
from models import db
from models.user import User
from models.vehicle import Vehicle
from models.showroom import Showroom
from models.inspector import Inspector
from models.booking import Booking

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_booking_workflow(client):
    with client.application.app_context():
        # Setup users and records
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
        db.session.commit()

        cust_id = cust.id
        veh_id = veh.id
        show_id = show.id
        insp_id = insp.id

    # Login as Customer
    client.post('/api/auth/login', json={'email': 'buyer@test.com', 'password': 'Password@123'})

    # Create Booking
    res = client.post('/api/bookings', json={
        'vehicle_id': veh_id,
        'showroom_id': show_id,
        'inspector_id': insp_id,
        'inspection_type': 'PREMIUM',
        'scheduled_date': str(date.today()),
        'scheduled_time': '10:30'
    })
    assert res.status_code == 201
    b_data = res.get_json()
    assert b_data['success'] is True
    booking_id = b_data['data']['id']

    # Login as Inspector
    client.post('/api/auth/login', json={'email': 'insp@test.com', 'password': 'Password@123'})

    # Accept Booking
    accept_res = client.post(f'/api/bookings/{booking_id}/accept')
    assert accept_res.status_code == 200
    assert accept_res.get_json()['success'] is True


def test_vehicle_creation_without_vin(client):
    with client.application.app_context():
        cust = User(name="Car Buyer", email="nobuyer@test.com", role="CUSTOMER")
        cust.set_password("Password@123")
        db.session.add(cust)
        db.session.commit()

    # Login as Customer
    client.post('/api/auth/login', json={'email': 'nobuyer@test.com', 'password': 'Password@123'})

    # Add Vehicle WITHOUT VIN (e.g. brand new car awaiting dealer VIN allotment)
    res = client.post('/api/vehicles', json={
        'brand': 'Mahindra',
        'model': 'XUV700',
        'variant': 'AX7L Diesel AT',
        'fuel_type': 'Diesel',
        'vehicle_type': 'ICE',
        'vin': ''
    })
    assert res.status_code == 201
    v_data = res.get_json()
    assert v_data['success'] is True
    assert v_data['data']['vin'].startswith('PENDING-')
