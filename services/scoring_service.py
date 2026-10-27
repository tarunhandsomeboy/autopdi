from models.inspection import Inspection, InspectionCategory
from models.checkpoint import InspectionCheckpoint
from models.inspector import Inspector

CATEGORY_WEIGHTS = {
    'Exterior': 0.20,
    'Paint': 0.20,
    'Glass': 0.20,
    'Interior': 0.15,
    'Mechanical': 0.25,
    'Engine': 0.25,
    'Transmission': 0.25,
    'Suspension': 0.25,
    'Brakes': 0.25,
    'EV Battery': 0.25,
    'EV Motor': 0.25,
    'Hybrid System': 0.25,
    'Electrical': 0.15,
    'EV Charging': 0.15,
    'Infotainment': 0.15,
    'AC': 0.15,
    'Safety': 0.15,
    'Road Test': 0.15,
    'Documents': 0.10,
    'Vehicle Identity': 0.10
}

# Standard 6 high-level buckets
MAJOR_BUCKETS = {
    'Exterior': ['Exterior', 'Paint', 'Glass', 'Wheels & Tires', 'Tires'],
    'Interior': ['Interior', 'AC', 'Infotainment'],
    'Mechanical': ['Mechanical', 'Engine', 'Transmission', 'Suspension', 'Brakes', 'EV Battery', 'EV Motor', 'Hybrid System'],
    'Electrical': ['Electrical', 'EV Charging', 'High Voltage Warning'],
    'Safety': ['Safety', 'Road Test', 'Regenerative Braking'],
    'Documents': ['Documents', 'Vehicle Identity']
}

BUCKET_WEIGHTS = {
    'Exterior': 0.20,
    'Interior': 0.15,
    'Mechanical': 0.25,
    'Electrical': 0.15,
    'Safety': 0.15,
    'Documents': 0.10
}

def calculate_inspection_readiness_score(inspection: Inspection):
    """
    Calculates the vehicle readiness score based on category weights and item statuses.
    Item scoring:
      PASS -> 100%
      ATTENTION -> 50%
      FAIL -> 0%
      NOT_APPLICABLE -> Excluded
    """
    checkpoints = inspection.checkpoints.all()
    if not checkpoints:
        return {
            'overall_score': 0.0,
            'final_status': 'HOLD_DELIVERY',
            'status_color': '#EF4444',
            'bucket_scores': {},
            'stats': {'pass': 0, 'attention': 0, 'fail': 0, 'total': 0},
            'ai_score': 0.0
        }

    stats = {'pass': 0, 'attention': 0, 'fail': 0, 'na': 0, 'total': len(checkpoints)}
    bucket_scores_map = {b: [] for b in MAJOR_BUCKETS.keys()}

    for cp in checkpoints:
        val = None
        if cp.status == 'PASS':
            val = 100.0
            stats['pass'] += 1
        elif cp.status == 'ATTENTION':
            val = 50.0
            stats['attention'] += 1
        elif cp.status == 'FAIL':
            val = 0.0
            stats['fail'] += 1
        else:
            stats['na'] += 1
            continue

        # Map to bucket
        cat_name = cp.category.name if cp.category else 'Exterior'
        assigned_bucket = 'Exterior'
        for b_name, cat_list in MAJOR_BUCKETS.items():
            if any(c.lower() in cat_name.lower() for c in cat_list):
                assigned_bucket = b_name
                break
        bucket_scores_map[assigned_bucket].append(val)

    # Calculate average for each bucket
    bucket_scores = {}
    weighted_sum = 0.0
    total_weight = 0.0

    for bucket, vals in bucket_scores_map.items():
        if vals:
            avg_score = sum(vals) / len(vals)
        else:
            avg_score = 100.0  # Default full score if no items in category
        bucket_scores[bucket] = round(avg_score, 1)
        w = BUCKET_WEIGHTS.get(bucket, 0.15)
        weighted_sum += avg_score * w
        total_weight += w

    overall_score = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0

    # Determine status & color
    if overall_score >= 90.0:
        final_status = 'DELIVERY_READY'
        status_color = '#10B981'  # Green
    elif overall_score >= 75.0:
        final_status = 'ATTENTION_REQUIRED'
        status_color = '#F59E0B'  # Amber / Yellow
    else:
        final_status = 'HOLD_DELIVERY'
        status_color = '#EF4444'  # Red

    # AI score
    ai_findings = inspection.ai_findings.all()
    if ai_findings:
        confirmed_count = sum(1 for f in ai_findings if f.inspector_confirmation == 'CONFIRMED')
        ai_score = max(0.0, 100.0 - (confirmed_count * 5.0))
    else:
        ai_score = overall_score

    return {
        'overall_score': overall_score,
        'final_status': final_status,
        'status_color': status_color,
        'bucket_scores': bucket_scores,
        'stats': stats,
        'ai_score': round(ai_score, 1)
    }


def calculate_inspector_trust_score(inspector: Inspector) -> int:
    """
    Computes an inspector trust score (0-100) based on:
    - Customer Rating (weight 35%)
    - Total Completed Inspections (weight 25%)
    - Verified Certifications (weight 20%)
    - Verified Equipment (weight 20%)
    """
    # Rating factor (0-100)
    rating_factor = (inspector.rating / 5.0) * 100.0

    # Inspection volume factor
    inspections_factor = min(100.0, (inspector.total_inspections / 50.0) * 100.0)

    # Verified Certifications
    certs = inspector.certifications.all()
    verified_certs = sum(1 for c in certs if c.verification_status == 'VERIFIED')
    cert_factor = min(100.0, verified_certs * 35.0) if certs else 70.0

    # Verified Equipment
    eqs = inspector.equipment_list.all()
    verified_eqs = sum(1 for e in eqs if e.verification_status == 'VERIFIED')
    eq_factor = min(100.0, verified_eqs * 25.0) if eqs else 70.0

    trust = (
        (rating_factor * 0.35) +
        (inspections_factor * 0.25) +
        (cert_factor * 0.20) +
        (eq_factor * 0.20)
    )
    return int(round(min(99, max(60, trust))))
