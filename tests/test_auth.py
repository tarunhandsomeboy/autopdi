import pytest
from app import create_app
from models import db
from models.user import User

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_user_registration(client):
    res = client.post('/api/auth/register', json={
        'name': 'Test Customer',
        'email': 'newcustomer@test.com',
        'phone': '+919876543210',
        'password': 'Password@123',
        'role': 'CUSTOMER'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['user']['email'] == 'newcustomer@test.com'

def test_user_login(client):
    # Register first
    client.post('/api/auth/register', json={
        'name': 'Test User',
        'email': 'loginuser@test.com',
        'phone': '+919876543210',
        'password': 'Password@123',
        'role': 'CUSTOMER'
    })

    # Login
    res = client.post('/api/auth/login', json={
        'email': 'loginuser@test.com',
        'password': 'Password@123'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'redirect_url' in data['data']
