from datetime import datetime
from models import db

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False)
    showroom_id = db.Column(db.Integer, db.ForeignKey('showrooms.id', ondelete='CASCADE'), nullable=False)
    inspector_id = db.Column(db.Integer, db.ForeignKey('inspectors.id', ondelete='SET NULL'), nullable=True)
    inspection_type = db.Column(db.String(20), nullable=False, default='PREMIUM')  # STANDARD, PREMIUM
    scheduled_date = db.Column(db.Date, nullable=False)
    scheduled_time = db.Column(db.Time, nullable=False)
    price = db.Column(db.Float, nullable=False, default=2499.00)
    status = db.Column(db.String(30), nullable=False, default='REQUESTED')  # REQUESTED, ACCEPTED, REJECTED, RESCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
    payment_status = db.Column(db.String(20), nullable=False, default='PAID')  # PENDING, PAID, REFUNDED
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    inspection = db.relationship('Inspection', backref='booking', uselist=False, cascade='all, delete-orphan')
    rating = db.relationship('Rating', backref='booking', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='booking', lazy='dynamic')

    def to_dict(self, include_nested=True):
        data = {
            'id': self.id,
            'customer_id': self.customer_id,
            'vehicle_id': self.vehicle_id,
            'showroom_id': self.showroom_id,
            'inspector_id': self.inspector_id,
            'inspection_type': self.inspection_type,
            'scheduled_date': self.scheduled_date.strftime('%Y-%m-%d') if self.scheduled_date else None,
            'scheduled_time': self.scheduled_time.strftime('%H:%M') if self.scheduled_time else None,
            'price': self.price,
            'status': self.status,
            'payment_status': self.payment_status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_nested:
            if self.customer:
                data['customer_name'] = self.customer.name
                data['customer_phone'] = self.customer.phone
                data['customer_email'] = self.customer.email
            if self.vehicle:
                data['vehicle'] = self.vehicle.to_dict()
            if self.showroom:
                data['showroom'] = self.showroom.to_dict()
            if self.inspector and self.inspector.user:
                data['inspector_name'] = self.inspector.user.name
                data['inspector_rating'] = self.inspector.rating
                data['inspector_trust_score'] = self.inspector.trust_score
                data['inspector_phone'] = self.inspector.user.phone
            if self.inspection:
                data['inspection_id'] = self.inspection.id
                data['overall_score'] = self.inspection.overall_score
                data['final_status'] = self.inspection.final_status
                data['verification_code'] = self.inspection.verification_code
            if self.rating:
                data['rating'] = self.rating.to_dict()
        return data

    def __repr__(self):
        return f"<Booking {self.id}: Customer {self.customer_id} -> Inspector {self.inspector_id} ({self.status})>"
