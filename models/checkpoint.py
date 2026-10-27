from datetime import datetime
from models import db

class InspectionCheckpoint(db.Model):
    __tablename__ = 'inspection_checkpoints'

    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('inspection_categories.id', ondelete='CASCADE'), nullable=False)
    item_name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='PASS')  # PASS, ATTENTION, FAIL, NOT_APPLICABLE
    severity = db.Column(db.String(20), nullable=False, default='LOW')  # LOW, MEDIUM, HIGH, CRITICAL
    remark = db.Column(db.Text, nullable=True)
    ai_detected = db.Column(db.Boolean, default=False)
    ai_confidence = db.Column(db.Float, nullable=True, default=0.0)
    inspector_verified = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    media = db.relationship('InspectionMedia', backref='checkpoint', lazy='dynamic', cascade='all, delete-orphan')
    ai_findings = db.relationship('AIFinding', backref='checkpoint', lazy='dynamic', cascade='all, delete-orphan')
    issues = db.relationship('IssueResolution', backref='checkpoint', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'inspection_id': self.inspection_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'General',
            'item_name': self.item_name,
            'status': self.status,
            'severity': self.severity,
            'remark': self.remark or '',
            'ai_detected': self.ai_detected,
            'ai_confidence': round(self.ai_confidence, 2) if self.ai_confidence else 0.0,
            'inspector_verified': self.inspector_verified,
            'media': [m.to_dict() for m in self.media.all()],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Checkpoint {self.id}: {self.item_name} [{self.status}]>"
