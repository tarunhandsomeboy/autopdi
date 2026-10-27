from datetime import datetime
from models import db

class Certification(db.Model):
    __tablename__ = 'certifications'

    id = db.Column(db.Integer, primary_key=True)
    inspector_id = db.Column(db.Integer, db.ForeignKey('inspectors.id', ondelete='CASCADE'), nullable=False)
    certificate_name = db.Column(db.String(150), nullable=False)
    issuer = db.Column(db.String(100), nullable=False)
    certificate_number = db.Column(db.String(100), nullable=True)
    issue_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    document_url = db.Column(db.String(255), nullable=True)
    verification_status = db.Column(db.String(20), nullable=False, default='PENDING')  # PENDING, VERIFIED, REJECTED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'inspector_id': self.inspector_id,
            'certificate_name': self.certificate_name,
            'issuer': self.issuer,
            'certificate_number': self.certificate_number,
            'issue_date': self.issue_date.strftime('%Y-%m-%d') if self.issue_date else None,
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d') if self.expiry_date else None,
            'document_url': self.document_url,
            'verification_status': self.verification_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Certification {self.id}: {self.certificate_name} ({self.verification_status})>"
