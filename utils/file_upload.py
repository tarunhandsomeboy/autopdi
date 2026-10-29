import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'pdf'}

def allowed_file(filename: str) -> bool:
    """Checks if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file_obj, target_dir: Path, prefix: str = 'media') -> tuple[str, Path]:
    """
    Saves an uploaded file safely with a unique filename.
    
    Returns:
        tuple[str, Path]: (web_accessible_url, absolute_saved_path)
    """
    os.makedirs(target_dir, exist_ok=True)

    original_name = secure_filename(file_obj.filename)
    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'jpg'
    
    unique_name = f"{prefix}_{uuid.uuid4().hex[:12]}_{original_name}"
    # Ensure safe filename
    safe_name = "".join([c for c in unique_name if c.isalnum() or c in ('_', '-', '.')])
    if not safe_name:
        safe_name = f"{prefix}_{uuid.uuid4().hex[:12]}.{ext}"

    dest_path = target_dir / safe_name
    file_obj.save(str(dest_path))

    # Determine URL path based on directory name
    dir_name = target_dir.name  # inspections, profiles, or documents
    web_url = f"/uploads/{dir_name}/{safe_name}"

    return web_url, dest_path
