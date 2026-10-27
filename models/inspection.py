from datetime import datetime
from models import db

class InspectionCategory(db.Model):
    __tablename__ = 'inspection_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    vehicle_type = db.Column(db.String(20), nullable=False, default='ALL')  # ALL, ICE, EV, HYBRID
    weight = db.Column(db.Float, nullable=False, default=15.0)              # Percentage weight
    description = db.Column(db.String(255), nullable=True)

    # Relationships
    checkpoints = db.relationship('InspectionCheckpoint', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'vehicle_type': self.vehicle_type,
            'weight': self.weight,
            'description': self.description
        }


class Inspection(db.Model):
    __tablename__ = 'inspections'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False, unique=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False)
    inspector_id = db.Column(db.Integer, db.ForeignKey('inspectors.id', ondelete='CASCADE'), nullable=False)
    vin_verified = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    overall_score = db.Column(db.Float, nullable=True, default=0.0)
    final_status = db.Column(db.String(30), nullable=False, default='ATTENTION_REQUIRED')  # DELIVERY_READY, ATTENTION_REQUIRED, HOLD_DELIVERY
    ai_score = db.Column(db.Float, nullable=True, default=0.0)
    inspection_hash = db.Column(db.String(64), nullable=True)
    verification_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    checkpoints = db.relationship('InspectionCheckpoint', backref='inspection', lazy='dynamic', cascade='all, delete-orphan')
    media_items = db.relationship('InspectionMedia', backref='inspection', lazy='dynamic', cascade='all, delete-orphan')
    ai_findings = db.relationship('AIFinding', backref='inspection', lazy='dynamic', cascade='all, delete-orphan')
    report = db.relationship('Report', backref='inspection', uselist=False, cascade='all, delete-orphan')
    issues = db.relationship('IssueResolution', backref='inspection', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_checkpoints=False):
        data = {
            'id': self.id,
            'booking_id': self.booking_id,
            'vehicle_id': self.vehicle_id,
            'inspector_id': self.inspector_id,
            'vin_verified': self.vin_verified,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'overall_score': round(self.overall_score, 1) if self.overall_score is not None else 0.0,
            'final_status': self.final_status,
            'ai_score': round(self.ai_score, 1) if self.ai_score is not None else 0.0,
            'inspection_hash': self.inspection_hash,
            'verification_code': self.verification_code,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_checkpoints:
            data['checkpoints'] = [cp.to_dict() for cp in self.checkpoints.all()]
            data['media'] = [m.to_dict() for m in self.media_items.all()]
            data['ai_findings'] = [f.to_dict() for f in self.ai_findings.all()]
        return data

    def __repr__(self):
        return f"<Inspection {self.id}: Code {self.verification_code} ({self.final_status})>"
