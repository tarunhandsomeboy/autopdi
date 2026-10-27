from datetime import datetime
from models import db

class Showroom(db.Model):
    __tablename__ = 'showrooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    latitude = db.Column(db.Float, nullable=True, default=12.9716)   # Default Bangalore coordinates
    longitude = db.Column(db.Float, nullable=True, default=77.5946)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='showroom', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'contact_number': self.contact_number,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Showroom {self.id}: {self.name} ({self.city})>"
