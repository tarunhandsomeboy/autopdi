import os
from flask import Blueprint, render_template, request, send_file, current_app
from models import db
from models.user import User
from models.inspection import Inspection
from models.report import Report
from models.rating import Rating
from models.booking import Booking
from services.report_service import generate_pdf_report
from services.scoring_service import calculate_inspector_trust_score
from utils.auth import login_required, role_required, get_current_user
from utils.helpers import success_response, error_response

report_bp = Blueprint('report', __name__)

@report_bp.route('/verify', methods=['GET'])
@report_bp.route('/verify/<string:verification_code>', methods=['GET'])
def verify_page(verification_code=None):
    inspection = None
    report = None
    if verification_code:
        clean_code = verification_code.strip().upper()
        inspection = Inspection.query.filter_by(verification_code=clean_code).first()
        if inspection:
            report = inspection.report

    return render_template(
        'verify_report.html',
        verification_code=verification_code,
        inspection=inspection,
        report=report
    )


@report_bp.route('/api/verify/<string:verification_code>', methods=['GET'])
def api_verify_report(verification_code):
    clean_code = verification_code.strip().upper()
    inspection = Inspection.query.filter_by(verification_code=clean_code).first()
    
    if not inspection:
        return error_response("Report verification failed. Invalid code.", 404)

    v = inspection.vehicle
    s = inspection.booking.showroom if inspection.booking else None
    insp = inspection.inspector

    return success_response(
        "Report verified successfully ✓",
        data={
            "verification_code": inspection.verification_code,
            "report_number": inspection.report.report_number if inspection.report else f"PDI-{inspection.id}",
            "vehicle": {
                "brand": v.brand,
                "model": v.model,
                "variant": v.variant,
                "vehicle_type": v.vehicle_type,
                "vin": v.vin[:6] + "******" + v.vin[-4:] if v.vin else "N/A"  # Masked for security
            },
            "inspection_date": inspection.completed_at.strftime('%d %b %Y, %I:%M %p') if inspection.completed_at else 'In Progress',
            "inspector_name": insp.user.name if insp and insp.user else 'Certified PDI Inspector',
            "overall_score": inspection.overall_score,
            "final_status": inspection.final_status,
            "inspection_hash": inspection.inspection_hash,
            "is_valid": True
        }
    )


@report_bp.route('/reports/<int:inspection_id>/pdf', methods=['GET'])
def download_pdf(inspection_id):
    inspection = Inspection.query.get_or_404(inspection_id)
    doc_folder = current_app.config['DOCUMENTS_UPLOAD_FOLDER']

    report = inspection.report
    if not report or not report.report_url or not os.path.exists(doc_folder / f"report_{inspection.verification_code}.pdf"):
        report = generate_pdf_report(inspection, doc_folder)

    pdf_filename = f"report_{inspection.verification_code}.pdf"
    pdf_path = doc_folder / pdf_filename

    if not os.path.exists(pdf_path):
        report = generate_pdf_report(inspection, doc_folder)

    return send_file(
        str(pdf_path),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"AUTO_PDI_{inspection.verification_code}.pdf"
    )


@report_bp.route('/api/reports/<int:inspection_id>/generate', methods=['POST'])
@login_required
def api_generate_report(inspection_id):
    inspection = Inspection.query.get_or_404(inspection_id)
    doc_folder = current_app.config['DOCUMENTS_UPLOAD_FOLDER']
    report = generate_pdf_report(inspection, doc_folder)
    return success_response("Report generated successfully", data=report.to_dict())


@report_bp.route('/api/ratings', methods=['POST'])
@role_required('CUSTOMER')
def api_submit_rating():
    user = get_current_user()
    data = request.get_json() or {}
    
    booking_id = data.get('booking_id')
    rating_val = float(data.get('rating', 5.0))
    review = data.get('review', '').strip()

    booking = Booking.query.filter_by(id=booking_id, customer_id=user.id).first_or_404()
    if not booking.inspector_id:
        return error_response("No inspector assigned to this booking.", 400)

    # Check if already rated
    existing_rating = Rating.query.filter_by(booking_id=booking.id).first()
    if existing_rating:
        existing_rating.rating = rating_val
        existing_rating.review = review
    else:
        rating_obj = Rating(
            booking_id=booking.id,
            customer_id=user.id,
            inspector_id=booking.inspector_id,
            rating=rating_val,
            review=review
        )
        db.session.add(rating_obj)

    # Recalculate Inspector average rating & trust score
    inspector = booking.inspector
    all_ratings = Rating.query.filter_by(inspector_id=inspector.id).all()
    if all_ratings:
        total_stars = sum(r.rating for r in all_ratings)
        inspector.rating = round(total_stars / len(all_ratings), 2)
    else:
        inspector.rating = rating_val

    inspector.trust_score = calculate_inspector_trust_score(inspector)
    db.session.commit()

    return success_response("Thank you for your rating!", data={"rating": rating_val, "inspector_rating": inspector.rating})
