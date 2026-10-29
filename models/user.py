from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='CUSTOMER')  # CUSTOMER, INSPECTOR, ADMIN
    profile_image = db.Column(db.String(255), nullable=True, default='/static/images/default-avatar.png')
    status = db.Column(db.String(20), nullable=False, default='ACTIVE')  # ACTIVE, INACTIVE, BLOCKED, PENDING
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicles = db.relationship('Vehicle', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    customer_bookings = db.relationship('Booking', backref='customer', lazy='dynamic', foreign_keys='Booking.customer_id')
    inspector_profile = db.relationship('Inspector', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='customer', lazy='dynamic', foreign_keys='Rating.customer_id')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'profile_image': self.profile_image,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_sensitive:
            data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data

    def __repr__(self):
        return f"<User {self.id}: {self.email} ({self.role})>"
