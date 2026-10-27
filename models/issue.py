from datetime import datetime
from models import db

class IssueResolution(db.Model):
    __tablename__ = 'issue_resolution'

    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey('inspection_checkpoints.id', ondelete='CASCADE'), nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default='OPEN')  # OPEN, DEALER_NOTIFIED, IN_PROGRESS, RESOLVED, CUSTOMER_VERIFIED
    dealer_response = db.Column(db.Text, nullable=True)
    resolution_image = db.Column(db.String(255), nullable=True)
    customer_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'inspection_id': self.inspection_id,
            'checkpoint_id': self.checkpoint_id,
            'checkpoint_name': self.checkpoint.item_name if self.checkpoint else 'Inspection Item',
            'severity': self.checkpoint.severity if self.checkpoint else 'MEDIUM',
            'issue_description': self.issue_description,
            'status': self.status,
            'dealer_response': self.dealer_response,
            'resolution_image': self.resolution_image,
            'customer_verified': self.customer_verified,
            'created_at': self.created_at.strftime('%d %b %Y, %I:%M %p') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%d %b %Y, %I:%M %p') if self.updated_at else None
        }

    def __repr__(self):
        return f"<IssueResolution {self.id}: Checkpoint {self.checkpoint_id} ({self.status})>"
