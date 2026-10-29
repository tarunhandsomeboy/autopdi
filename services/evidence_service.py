import hashlib
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def format_evidence_timestamp(dt: datetime = None) -> str:
    """Returns human-friendly timestamp formatted as '22 Aug 2026, 10:43 AM'."""
    if not dt:
        dt = datetime.utcnow()
    return dt.strftime('%d %b %Y, %I:%M %p')


def calculate_file_sha256(filepath: str) -> str:
    """Computes SHA-256 hash for file tamper verification."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def extract_exif_gps_coordinates(image_path: str):
    """Extracts latitude and longitude from image EXIF metadata if available."""
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if not exif_data:
                return None, None

            gps_info = {}
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "GPSInfo":
                    for gps_tag_id in value:
                        sub_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_info[sub_tag_name] = value[gps_tag_id]

            if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
                lat = _convert_to_degrees(gps_info['GPSLatitude'])
                if gps_info.get('GPSLatitudeRef', 'N') != 'N':
                    lat = -lat

                lon = _convert_to_degrees(gps_info['GPSLongitude'])
                if gps_info.get('GPSLongitudeRef', 'E') != 'E':
                    lon = -lon
                return round(lat, 6), round(lon, 6)
    except Exception:
        pass
    return None, None


def _convert_to_degrees(value):
    """Helper function to convert GPS coordinates to degrees."""
    d0 = value[0]
    d1 = value[1]
    d2 = value[2]
    return float(d0) + (float(d1) / 60.0) + (float(d2) / 3600.0)
