"""Upload router — handles image and video file uploads."""

import os
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Inspection, MediaFile
from ..schemas import UploadResponse
from ..services.storage import save_upload, get_file_size

router = APIRouter(prefix="/api/upload", tags=["uploads"])


@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload an image file for inspection."""
    # Validate file type
    allowed = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported image format: {ext}. Allowed: {allowed}")

    # Read and save file
    content = await file.read()
    file_id, file_path = save_upload(content, file.filename or "image.jpg")

    # Create inspection record
    inspection = Inspection(inspection_type="image", status="pending")
    db.add(inspection)
    await db.flush()

    # Create media file record
    media = MediaFile(
        inspection_id=inspection.id,
        file_path=file_path,
        file_name=file.filename or "image.jpg",
        file_type="image",
        file_size=len(content),
    )
    db.add(media)
    await db.flush()

    return UploadResponse(
        inspection_id=inspection.id,
        file_id=media.id,
        message="Image uploaded successfully. Ready for detection.",
    )


@router.post("/video", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a video file for inspection."""
    allowed = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported video format: {ext}. Allowed: {allowed}")

    content = await file.read()
    file_id, file_path = save_upload(content, file.filename or "video.mp4")

    inspection = Inspection(inspection_type="video", status="pending")
    db.add(inspection)
    await db.flush()

    media = MediaFile(
        inspection_id=inspection.id,
        file_path=file_path,
        file_name=file.filename or "video.mp4",
        file_type="video",
        file_size=len(content),
    )
    db.add(media)
    await db.flush()

    return UploadResponse(
        inspection_id=inspection.id,
        file_id=media.id,
        message="Video uploaded successfully. Ready for detection.",
    )
