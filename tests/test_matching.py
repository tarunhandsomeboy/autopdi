import pytest
from app import create_app
from models import db
from models.user import User
from models.inspector import Inspector, InspectorSpecialization
from models.showroom import Showroom
from models.vehicle import Vehicle
from models.equipment import Equipment
from services.matching_service import rank_inspectors_for_booking, calculate_skill_score, calculate_equipment_score

@pytest.fixture
def app_ctx():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

def test_matching_algorithm(app_ctx):
    # Create Inspector User
    u = User(name="Top Diagnostic Pro", email="top@pdi.com", role="INSPECTOR", status="ACTIVE")
    u.set_password("Password@123")
    db.session.add(u)
    db.session.flush()

    insp = Inspector(
        user_id=u.id,
        experience_years=8,
        total_inspections=500,
        rating=4.9,
        trust_score=95,
        verification_status="VERIFIED",
        availability_status="AVAILABLE",
        latitude=12.9716,
        longitude=77.5946,
        specialization="ICE, EV - Hyundai, Tata"
    )
    db.session.add(insp)
    db.session.flush()

    # Add verified equipment
    eq1 = Equipment(inspector_id=insp.id, equipment_name="Paint Thickness Gauge", verification_status="VERIFIED")
    eq2 = Equipment(inspector_id=insp.id, equipment_name="OBD-II Scanner", verification_status="VERIFIED")
    db.session.add_all([eq1, eq2])

    # Showroom and Vehicle
    showroom = Showroom(name="City Showroom", address="MG Road", city="Bangalore", latitude=12.9716, longitude=77.5946)
    customer = User(name="Buyer", email="buyer@test.com", role="CUSTOMER")
    customer.set_password("Password@123")
    db.session.add_all([showroom, customer])
    db.session.flush()

    vehicle = Vehicle(customer_id=customer.id, brand="Hyundai", model="Creta", vehicle_type="ICE", vin="VINTEST12345")
    db.session.add(vehicle)
    db.session.commit()

    # Run matching service
    results = rank_inspectors_for_booking(vehicle, showroom, 'PREMIUM')
    assert len(results) >= 1
    top_match = results[0]
    assert top_match['match_score'] >= 80.0
    assert top_match['inspector']['name'] == "Top Diagnostic Pro"
