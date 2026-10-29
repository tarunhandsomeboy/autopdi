from datetime import datetime
from models import db

class AIFinding(db.Model):
    __tablename__ = 'ai_findings'

    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey('inspection_checkpoints.id', ondelete='CASCADE'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('inspection_media.id', ondelete='SET NULL'), nullable=True)
    finding_type = db.Column(db.String(100), nullable=False)  # Scratch, Dent, Paint Thickness, Panel Gap, Rust, etc.
    description = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, nullable=False, default=0.85)  # 0.00 to 1.00
    severity = db.Column(db.String(20), nullable=False, default='LOW')  # LOW, MEDIUM, HIGH, CRITICAL
    inspector_confirmation = db.Column(db.String(20), nullable=False, default='PENDING')  # PENDING, CONFIRMED, REJECTED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'inspection_id': self.inspection_id,
            'checkpoint_id': self.checkpoint_id,
            'image_id': self.image_id,
            'finding_type': self.finding_type,
            'description': self.description,
            'confidence': round(self.confidence * 100, 1),
            'severity': self.severity,
            'inspector_confirmation': self.inspector_confirmation,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<AIFinding {self.id}: {self.finding_type} ({self.inspector_confirmation})>"
