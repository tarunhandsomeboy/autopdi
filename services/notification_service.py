from models import db
from models.notification import Notification
from models.user import User

def create_notification(user_id: int, title: str, message: str, notif_type: str = 'INFO', booking_id: int = None):
    """Dispatches an in-app notification to a user."""
    try:
        notif = Notification(
            user_id=user_id,
            booking_id=booking_id,
            title=title,
            message=message,
            type=notif_type
        )
        db.session.add(notif)
        db.session.commit()
        return notif
    except Exception as e:
        db.session.rollback()
        return None


def notify_admin(title: str, message: str, notif_type: str = 'INFO', booking_id: int = None):
    """Dispatches a notification to all admin users."""
    admins = User.query.filter_by(role='ADMIN').all()
    for admin in admins:
        create_notification(admin.id, title, message, notif_type, booking_id)
