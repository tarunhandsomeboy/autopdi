import math
from models.inspector import Inspector, InspectorSpecialization
from models.showroom import Showroom
from models.vehicle import Vehicle

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth in kilometers."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 10.0  # default reasonable distance if coordinates missing

    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


def calculate_skill_score(inspector, vehicle: Vehicle) -> float:
    """Calculate skill match score (0-100) based on vehicle type and brand specializations."""
    base_score = 60.0
    v_type = (vehicle.vehicle_type or 'ICE').upper()
    v_brand = (vehicle.brand or '').lower()

    specializations = inspector.specializations.all()
    if not specializations:
        # Check text specialization field
        spec_text = (inspector.specialization or '').upper()
        if v_type in spec_text:
            base_score += 25.0
        if v_brand in (inspector.specialization or '').lower():
            base_score += 15.0
        return min(100.0, base_score)

    has_type_match = any(s.vehicle_type.upper() == v_type or s.vehicle_type.upper() == 'ALL' for s in specializations)
    has_brand_match = any((s.brand or '').lower() == v_brand or (s.brand or '').lower() == 'all' for s in specializations)

    if has_type_match:
        base_score += 25.0
    if has_brand_match:
        base_score += 15.0

    return min(100.0, base_score)


def calculate_equipment_score(inspector, inspection_type: str = 'PREMIUM') -> float:
    """Calculate equipment match score (0-100) based on verified equipment inventory."""
    verified_eq = [e.equipment_name.lower() for e in inspector.equipment_list.filter_by(verification_status='VERIFIED').all()]
    
    if not verified_eq:
        # Fallback to total equipment if verification pending in demo
        verified_eq = [e.equipment_name.lower() for e in inspector.equipment_list.all()]

    if inspection_type.upper() == 'STANDARD':
        required_tools = ['paint thickness gauge', 'obd-ii scanner', 'tire depth gauge']
    else:
        # Premium requires diagnostic scanner, paint depth gauge, battery tester, multimeter/thermal camera
        required_tools = ['paint thickness gauge', 'obd-ii scanner', 'battery tester', 'tire depth gauge', 'thermal camera', 'ev diagnostic scanner']

    matched = 0
    for req in required_tools:
        if any(req in eq or eq in req for eq in verified_eq):
            matched += 1

    if not required_tools:
        return 80.0

    ratio = matched / len(required_tools)
    return min(100.0, max(50.0, ratio * 100.0 + 20.0))


def calculate_distance_score(distance_km: float) -> float:
    """Normalize distance to score (0-100). Closer is better."""
    if distance_km <= 3.0:
        return 100.0
    elif distance_km <= 15.0:
        return max(70.0, 100.0 - (distance_km - 3.0) * 2.5)
    elif distance_km <= 40.0:
        return max(40.0, 70.0 - (distance_km - 15.0) * 1.2)
    else:
        return max(15.0, 40.0 - (distance_km - 40.0) * 0.5)


def calculate_experience_score(experience_years: int) -> float:
    """Normalize experience years to score (0-100). 10+ years = 100%."""
    return min(100.0, max(20.0, (experience_years / 10.0) * 100.0))


def calculate_rating_score(rating: float) -> float:
    """Normalize 1-5 rating to 0-100%."""
    return min(100.0, max(0.0, (rating / 5.0) * 100.0))


def calculate_availability_score(status: str) -> float:
    """Score availability status."""
    st = (status or 'AVAILABLE').upper()
    if st == 'AVAILABLE':
        return 100.0
    elif st == 'BUSY':
        return 40.0
    return 10.0


def rank_inspectors_for_booking(vehicle: Vehicle, showroom: Showroom, inspection_type: str = 'PREMIUM'):
    """
    Core Match Score Algorithm:
    match_score = (skill * 0.30) + (equipment * 0.25) + (distance * 0.15) + 
                  (experience * 0.10) + (rating * 0.10) + (availability * 0.10)
    """
    inspectors = Inspector.query.filter(Inspector.verification_status.in_(['VERIFIED', 'PENDING'])).all()
    results = []

    s_lat = showroom.latitude if showroom else 12.9716
    s_lon = showroom.longitude if showroom else 77.5946

    for insp in inspectors:
        distance_km = haversine_distance(insp.latitude, insp.longitude, s_lat, s_lon)

        skill_score = calculate_skill_score(insp, vehicle)
        equipment_score = calculate_equipment_score(insp, inspection_type)
        distance_score = calculate_distance_score(distance_km)
        experience_score = calculate_experience_score(insp.experience_years)
        rating_score = calculate_rating_score(insp.rating)
        avail_score = calculate_availability_score(insp.availability_status)

        match_score = (
            (skill_score * 0.30) +
            (equipment_score * 0.25) +
            (distance_score * 0.15) +
            (experience_score * 0.10) +
            (rating_score * 0.10) +
            (avail_score * 0.10)
        )
        match_score = round(min(99.4, max(50.0, match_score)), 1)

        price = insp.price_premium if inspection_type.upper() == 'PREMIUM' else insp.price_standard

        results.append({
            'inspector': insp.to_dict(include_details=True),
            'match_score': match_score,
            'breakdown': {
                'skill_score': round(skill_score, 1),
                'equipment_score': round(equipment_score, 1),
                'distance_score': round(distance_score, 1),
                'experience_score': round(experience_score, 1),
                'rating_score': round(rating_score, 1),
                'availability_score': round(avail_score, 1)
            },
            'distance_km': distance_km,
            'price': price
        })

    # Sort descending by match score
    results.sort(key=lambda x: x['match_score'], reverse=True)
    return results
