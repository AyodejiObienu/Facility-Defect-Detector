"""File storage abstraction — local disk for now, swappable to S3/R2."""

import os
import shutil
import uuid
from pathlib import Path

from ..config import settings


def _ensure_dirs():
    """Create upload and results directories if they don't exist."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.RESULTS_DIR, exist_ok=True)


def save_upload(file_bytes: bytes, original_filename: str) -> tuple[str, str]:
    """
    Save an uploaded file to the uploads directory.

    Returns:
        (file_id, file_path) — the unique ID and full path to the saved file.
    """
    _ensure_dirs()
    ext = Path(original_filename).suffix.lower()
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return file_id, file_path


def get_file_path(file_id: str, extension: str = "") -> str:
    """Get the full path for a file by its ID."""
    if extension and not extension.startswith("."):
        extension = f".{extension}"
    return os.path.join(settings.UPLOAD_DIR, f"{file_id}{extension}")


def delete_file(file_path: str) -> bool:
    """Delete a file from storage."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except OSError:
        pass
    return False


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0
