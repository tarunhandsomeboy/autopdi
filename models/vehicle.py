from datetime import datetime
from models import db

class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    brand = db.Column(db.String(50), nullable=False)  # Hyundai, Tata, Mahindra, Kia, etc.
    model = db.Column(db.String(50), nullable=False)  # Creta, Nexon EV, Thar, Seltos, etc.
    variant = db.Column(db.String(50), nullable=True)  # SX(O), Fearless+, etc.
    fuel_type = db.Column(db.String(30), nullable=False, default='Petrol')  # Petrol, Diesel, Electric, Hybrid, CNG
    vehicle_type = db.Column(db.String(20), nullable=False, default='ICE')  # ICE, EV, HYBRID
    vin = db.Column(db.String(50), nullable=False, index=True)
    registration_number = db.Column(db.String(50), nullable=True)
    manufacturing_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='vehicle', lazy='dynamic')
    inspections = db.relationship('Inspection', backref='vehicle', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'brand': self.brand,
            'model': self.model,
            'variant': self.variant,
            'fuel_type': self.fuel_type,
            'vehicle_type': self.vehicle_type,
            'vin': self.vin,
            'registration_number': self.registration_number,
            'manufacturing_date': self.manufacturing_date.strftime('%Y-%m-%d') if self.manufacturing_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Vehicle {self.id}: {self.brand} {self.model} ({self.vehicle_type})>"
