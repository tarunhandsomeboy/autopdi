import random
import string
from datetime import datetime
from flask import jsonify

def generate_verification_code() -> str:
    """Generates an authentic alphanumeric verification code: PDI-2026-XXXXX"""
    year = datetime.utcnow().year
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"PDI-{year}-{suffix}"


def generate_report_number(inspection_id: int) -> str:
    """Generates unique report sequence number."""
    year = datetime.utcnow().year
    return f"PDI-REP-{year}-{inspection_id:05d}"


def success_response(message: str = "Success", data=None, status_code: int = 200):
    """Standardized JSON success response."""
    payload = {
        "success": True,
        "message": message,
        "data": data if data is not None else {}
    }
    return jsonify(payload), status_code


def error_response(message: str = "An error occurred", status_code: int = 400, errors=None):
    """Standardized JSON error response."""
    payload = {
        "success": False,
        "message": message
    }
    if errors is not None:
        payload["errors"] = errors
    return jsonify(payload), status_code


def format_currency(amount: float) -> str:
    """Formats amount as Indian Rupee / standard currency."""
    return f"₹{amount:,.2f}"
