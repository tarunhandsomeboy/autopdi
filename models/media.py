from datetime import datetime
from models import db

class InspectionMedia(db.Model):
    __tablename__ = 'inspection_media'

    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey('inspection_checkpoints.id', ondelete='SET NULL'), nullable=True)
    file_url = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), nullable=False, default='IMAGE')  # IMAGE, DOCUMENT, VIDEO
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    captured_at = db.Column(db.DateTime, default=datetime.utcnow)
    ai_analysis = db.Column(db.Text, nullable=True)
    ai_confidence = db.Column(db.Float, nullable=True, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    ai_findings = db.relationship('AIFinding', backref='image', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'inspection_id': self.inspection_id,
            'checkpoint_id': self.checkpoint_id,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'captured_at': self.captured_at.strftime('%d %b %Y, %I:%M %p') if self.captured_at else None,
            'ai_analysis': self.ai_analysis,
            'ai_confidence': round(self.ai_confidence, 2) if self.ai_confidence else 0.0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<InspectionMedia {self.id}: {self.file_url}>"
