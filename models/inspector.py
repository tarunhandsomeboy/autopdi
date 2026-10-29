from datetime import datetime
from models import db

class Inspector(db.Model):
    __tablename__ = 'inspectors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    bio = db.Column(db.Text, nullable=True)
    experience_years = db.Column(db.Integer, nullable=False, default=1)
    total_inspections = db.Column(db.Integer, nullable=False, default=0)
    rating = db.Column(db.Float, nullable=False, default=5.0)
    trust_score = db.Column(db.Integer, nullable=False, default=90)  # 0-100
    verification_status = db.Column(db.String(20), nullable=False, default='PENDING')  # PENDING, VERIFIED, REJECTED, SUSPENDED
    availability_status = db.Column(db.String(20), nullable=False, default='AVAILABLE')  # AVAILABLE, BUSY, OFFLINE
    latitude = db.Column(db.Float, nullable=True, default=12.9716)
    longitude = db.Column(db.Float, nullable=True, default=77.5946)
    specialization = db.Column(db.String(255), nullable=True, default='ICE, EV, Hybrid')
    price_standard = db.Column(db.Float, nullable=False, default=1499.00)
    price_premium = db.Column(db.Float, nullable=False, default=2499.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    equipment_list = db.relationship('Equipment', backref='inspector', lazy='dynamic', cascade='all, delete-orphan')
    certifications = db.relationship('Certification', backref='inspector', lazy='dynamic', cascade='all, delete-orphan')
    specializations = db.relationship('InspectorSpecialization', backref='inspector', lazy='dynamic', cascade='all, delete-orphan')
    availabilities = db.relationship('InspectorAvailability', backref='inspector', lazy='dynamic', cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='inspector', lazy='dynamic')
    inspections = db.relationship('Inspection', backref='inspector', lazy='dynamic')
    ratings = db.relationship('Rating', backref='inspector', lazy='dynamic')

    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.name if self.user else 'Unknown',
            'email': self.user.email if self.user else '',
            'phone': self.user.phone if self.user else '',
            'profile_image': self.user.profile_image if self.user else '/static/images/default-avatar.png',
            'bio': self.bio,
            'experience_years': self.experience_years,
            'total_inspections': self.total_inspections,
            'rating': round(self.rating, 2),
            'trust_score': self.trust_score,
            'verification_status': self.verification_status,
            'availability_status': self.availability_status,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'specialization': self.specialization,
            'price_standard': self.price_standard,
            'price_premium': self.price_premium,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_details:
            data['equipment'] = [eq.to_dict() for eq in self.equipment_list.all()]
            data['certifications'] = [cert.to_dict() for cert in self.certifications.all()]
            data['specializations'] = [spec.to_dict() for spec in self.specializations.all()]
        return data

    def __repr__(self):
        return f"<Inspector {self.id}: User {self.user_id} ({self.verification_status})>"


class InspectorSpecialization(db.Model):
    __tablename__ = 'inspector_specializations'

    id = db.Column(db.Integer, primary_key=True)
    inspector_id = db.Column(db.Integer, db.ForeignKey('inspectors.id', ondelete='CASCADE'), nullable=False)
    brand = db.Column(db.String(50), nullable=True)          # e.g., Hyundai, Tata, All
    vehicle_type = db.Column(db.String(20), nullable=False)   # ICE, EV, HYBRID
    skill_level = db.Column(db.String(20), nullable=False, default='EXPERT')  # BEGINNER, INTERMEDIATE, EXPERT, MASTER

    def to_dict(self):
        return {
            'id': self.id,
            'inspector_id': self.inspector_id,
            'brand': self.brand,
            'vehicle_type': self.vehicle_type,
            'skill_level': self.skill_level
        }


class InspectorAvailability(db.Model):
    __tablename__ = 'availability'

    id = db.Column(db.Integer, primary_key=True)
    inspector_id = db.Column(db.Integer, db.ForeignKey('inspectors.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'inspector_id': self.inspector_id,
            'date': self.date.strftime('%Y-%m-%d'),
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'is_available': self.is_available
        }
