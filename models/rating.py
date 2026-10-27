from datetime import datetime
from models import db

class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    inspector_id = db.Column(db.Integer, db.ForeignKey('inspectors.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Float, nullable=False, default=5.0)  # 1.0 to 5.0
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else 'Customer',
            'inspector_id': self.inspector_id,
            'rating': self.rating,
            'review': self.review,
            'created_at': self.created_at.strftime('%d %b %Y') if self.created_at else None
        }

    def __repr__(self):
        return f"<Rating {self.id}: {self.rating} stars for Inspector {self.inspector_id}>"
