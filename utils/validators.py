import re

def validate_email(email: str) -> bool:
    """Validates email format."""
    if not email:
        return False
    regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(regex, email.strip()))


def validate_phone(phone: str) -> bool:
    """Validates phone number format."""
    if not phone:
        return False
    # Allow digits, optional leading +, spaces and dashes, minimum 7 digits
    clean = re.sub(r'[\s\-\(\)\+]', '', phone)
    return len(clean) >= 7 and clean.isdigit()


def validate_vin(vin: str) -> bool:
    """Validates vehicle identification number (alphanumeric, 5-17 characters for demo flexibility)."""
    if not vin:
        return False
    clean = vin.strip().upper()
    # Remove I, O, Q standard if 17 chars, but allow standard alphanumeric
    return bool(re.match(r'^[A-HJ-NPR-Z0-9]{5,17}$', clean))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validates basic password security."""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""
