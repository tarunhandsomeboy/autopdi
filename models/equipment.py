from datetime import datetime
from models import db

class Equipment(db.Model):
    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True)
    inspector_id = db.Column(db.Integer, db.ForeignKey('inspectors.id', ondelete='CASCADE'), nullable=False)
    equipment_name = db.Column(db.String(100), nullable=False)  # OBD-II Scanner, Paint Thickness Gauge, etc.
    equipment_type = db.Column(db.String(50), nullable=True)    # DIAGNOSTIC, SENSOR, OPTICAL, ELECTRICAL
    serial_number = db.Column(db.String(100), nullable=True)
    verification_status = db.Column(db.String(20), nullable=False, default='PENDING')  # PENDING, VERIFIED, REJECTED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'inspector_id': self.inspector_id,
            'equipment_name': self.equipment_name,
            'equipment_type': self.equipment_type,
            'serial_number': self.serial_number,
            'verification_status': self.verification_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Equipment {self.id}: {self.equipment_name} ({self.verification_status})>"
