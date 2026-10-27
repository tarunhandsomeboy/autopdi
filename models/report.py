from datetime import datetime
from models import db

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False, unique=True)
    report_number = db.Column(db.String(50), unique=True, nullable=False)
    overall_score = db.Column(db.Float, nullable=False)
    report_url = db.Column(db.String(255), nullable=True)  # PDF URL path
    verification_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    report_hash = db.Column(db.String(64), nullable=False)  # SHA-256 integrity hash
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'inspection_id': self.inspection_id,
            'report_number': self.report_number,
            'overall_score': round(self.overall_score, 1),
            'report_url': self.report_url,
            'verification_code': self.verification_code,
            'report_hash': self.report_hash,
            'generated_at': self.generated_at.strftime('%d %b %Y, %I:%M %p') if self.generated_at else None
        }

    def __repr__(self):
        return f"<Report {self.id}: {self.report_number} (Score: {self.overall_score})>"
