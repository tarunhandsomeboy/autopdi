from datetime import datetime
from flask import Blueprint, request
from models import db
from models.issue import IssueResolution
from models.inspection import Inspection
from models.booking import Booking
from services.notification_service import create_notification
from utils.auth import login_required, get_current_user
from utils.helpers import success_response, error_response

issue_bp = Blueprint('issue', __name__)

@issue_bp.route('/api/issues', methods=['GET'])
@login_required
def api_get_issues():
    user = get_current_user()
    
    if user.role == 'CUSTOMER':
        issues = (
            IssueResolution.query.join(Inspection).join(Booking)
            .filter(Booking.customer_id == user.id)
            .order_by(IssueResolution.created_at.desc())
            .all()
        )
    elif user.role == 'INSPECTOR':
        inspector = user.inspector_profile
        issues = (
            IssueResolution.query.join(Inspection)
            .filter(Inspection.inspector_id == inspector.id)
            .order_by(IssueResolution.created_at.desc())
            .all()
        )
    else:  # ADMIN
        issues = IssueResolution.query.order_by(IssueResolution.created_at.desc()).all()

    return success_response("Issues list", data=[issue.to_dict() for issue in issues])


@issue_bp.route('/api/issues/<int:issue_id>/status', methods=['PUT'])
@login_required
def api_update_issue_status(issue_id):
    issue = IssueResolution.query.get_or_404(issue_id)
    data = request.get_json() or {}
    
    new_status = data.get('status', issue.status).upper()
    dealer_response = data.get('dealer_response', issue.dealer_response)
    resolution_image = data.get('resolution_image', issue.resolution_image)

    allowed_statuses = ['OPEN', 'DEALER_NOTIFIED', 'IN_PROGRESS', 'RESOLVED', 'CUSTOMER_VERIFIED']
    if new_status not in allowed_statuses:
        return error_response(f"Invalid status. Must be one of {allowed_statuses}", 400)

    issue.status = new_status
    if dealer_response:
        issue.dealer_response = dealer_response
    if resolution_image:
        issue.resolution_image = resolution_image
    issue.updated_at = datetime.utcnow()

    db.session.commit()

    # If resolved, notify customer
    if new_status == 'RESOLVED' and issue.inspection and issue.inspection.booking:
        create_notification(
            user_id=issue.inspection.booking.customer_id,
            booking_id=issue.inspection.booking_id,
            title="Dealer Issue Resolved",
            message=f"The dealer has marked '{issue.checkpoint.item_name if issue.checkpoint else 'Flagged item'}' as resolved. Please inspect and verify.",
            notif_type='SUCCESS'
        )

    return success_response("Issue status updated", data=issue.to_dict())


@issue_bp.route('/api/issues/<int:issue_id>/verify', methods=['PUT'])
@login_required
def api_verify_issue(issue_id):
    user = get_current_user()
    issue = IssueResolution.query.get_or_404(issue_id)

    issue.status = 'CUSTOMER_VERIFIED'
    issue.customer_verified = True
    issue.updated_at = datetime.utcnow()
    db.session.commit()

    return success_response("Issue verified by customer ✓", data=issue.to_dict())
