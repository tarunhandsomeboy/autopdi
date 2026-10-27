from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models to ensure registration with SQLAlchemy
from models.user import User
from models.vehicle import Vehicle
from models.showroom import Showroom
from models.inspector import Inspector, InspectorSpecialization, InspectorAvailability
from models.equipment import Equipment
from models.certification import Certification
from models.booking import Booking
from models.inspection import Inspection, InspectionCategory
from models.checkpoint import InspectionCheckpoint
from models.media import InspectionMedia
from models.ai_finding import AIFinding
from models.report import Report
from models.rating import Rating
from models.notification import Notification
from models.issue import IssueResolution

__all__ = [
    'db',
    'User',
    'Vehicle',
    'Showroom',
    'Inspector',
    'InspectorSpecialization',
    'InspectorAvailability',
    'Equipment',
    'Certification',
    'Booking',
    'Inspection',
    'InspectionCategory',
    'InspectionCheckpoint',
    'InspectionMedia',
    'AIFinding',
    'Report',
    'Rating',
    'Notification',
    'IssueResolution'
]
