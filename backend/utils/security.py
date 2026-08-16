import os
import re
from fastapi import HTTPException, UploadFile
from backend.config import settings

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes file name to prevent path traversal, command injection,
    and invalid filesystem characters.
    """
    # Base filename only (removes path directory components)
    basename = os.path.basename(filename)
    # Remove null bytes
    basename = basename.replace('\x00', '')
    # Replace non-alphanumeric (except dots, underscores, dashes)
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', basename)
    return sanitized

def validate_uploaded_file(file: UploadFile, file_size: int):
    """
    Validates file extension, MIME type, and file size boundaries.
    """
    filename = file.filename or ""
    sanitized = sanitize_filename(filename)
    
    ext = sanitized.split('.')[-1].lower() if '.' in sanitized else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats are: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
        
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

def secure_filepath_join(base_dir: str, filename: str) -> str:
    """
    Safely joins directory path and filename preventing directory traversal attacks.
    """
    sanitized = sanitize_filename(filename)
    safe_path = os.path.abspath(os.path.join(base_dir, sanitized))
    base_abs = os.path.abspath(base_dir)
    
    if not safe_path.startswith(base_abs):
        raise HTTPException(status_code=400, detail="Invalid path traversal detected.")
        
    return safe_path
