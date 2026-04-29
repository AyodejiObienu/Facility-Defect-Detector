"""Detection router — runs ML inference on uploaded media or webcam frames."""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Inspection, Detection, MediaFile
from ..schemas import DetectResponse, DetectionBase, FrameDetectRequest
from ..services.inference import detect_image, detect_frame, detect_video

router = APIRouter(prefix="/api/detect", tags=["detection"])


@router.post("/image/{inspection_id}", response_model=DetectResponse)
async def run_image_detection(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run YOLO detection on an uploaded image."""
    # Fetch the inspection with media files
    result = await db.execute(
        select(Inspection)
        .options(selectinload(Inspection.media_files))
        .where(Inspection.id == inspection_id)
    )
    inspection = result.scalar_one_or_none()
    if not inspection:
        raise HTTPException(404, "Inspection not found")

    if not inspection.media_files:
        raise HTTPException(400, "No media file associated with this inspection")

    media = inspection.media_files[0]

    # Update status
    inspection.status = "processing"
    await db.flush()

    # Run detection
    try:
        detections = detect_image(media.file_path)
    except Exception as e:
        inspection.status = "failed"
        await db.flush()
        raise HTTPException(500, f"Detection failed: {str(e)}")

    # Save detections to DB
    anomaly_count = 0
    for det in detections:
        db_det = Detection(
            inspection_id=inspection_id,
            class_name=det["class_name"],
            confidence=det["confidence"],
            is_anomaly=det["is_anomaly"],
            bbox_x1=det["bbox_x1"],
            bbox_y1=det["bbox_y1"],
            bbox_x2=det["bbox_x2"],
            bbox_y2=det["bbox_y2"],
        )
        if det["is_anomaly"]:
            anomaly_count += 1
        db.add(db_det)

    inspection.status = "completed"
    inspection.total_anomalies = anomaly_count
    inspection.completed_at = datetime.now(timezone.utc)
    await db.flush()

    return DetectResponse(
        inspection_id=inspection_id,
        total_detections=len(detections),
        anomaly_count=anomaly_count,
        detections=[DetectionBase(**d) for d in detections],
    )


@router.post("/video/{inspection_id}", response_model=DetectResponse)
async def run_video_detection(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run YOLO detection on an uploaded video (frame sampling)."""
    result = await db.execute(
        select(Inspection)
        .options(selectinload(Inspection.media_files))
        .where(Inspection.id == inspection_id)
    )
    inspection = result.scalar_one_or_none()
    if not inspection:
        raise HTTPException(404, "Inspection not found")

    if not inspection.media_files:
        raise HTTPException(400, "No media file associated with this inspection")

    media = inspection.media_files[0]

    inspection.status = "processing"
    await db.flush()

    try:
        detections = detect_video(media.file_path)
    except Exception as e:
        inspection.status = "failed"
        await db.flush()
        raise HTTPException(500, f"Detection failed: {str(e)}")

    anomaly_count = 0
    for det in detections:
        db_det = Detection(
            inspection_id=inspection_id,
            class_name=det["class_name"],
            confidence=det["confidence"],
            is_anomaly=det["is_anomaly"],
            bbox_x1=det["bbox_x1"],
            bbox_y1=det["bbox_y1"],
            bbox_x2=det["bbox_x2"],
            bbox_y2=det["bbox_y2"],
            frame_number=det.get("frame_number"),
        )
        if det["is_anomaly"]:
            anomaly_count += 1
        db.add(db_det)

    inspection.status = "completed"
    inspection.total_anomalies = anomaly_count
    inspection.completed_at = datetime.now(timezone.utc)
    await db.flush()

    return DetectResponse(
        inspection_id=inspection_id,
        total_detections=len(detections),
        anomaly_count=anomaly_count,
        detections=[DetectionBase(**d) for d in detections],
    )


@router.post("/frame", response_model=DetectResponse)
async def run_frame_detection(
    body: FrameDetectRequest,
    db: AsyncSession = Depends(get_db),
):
    """Run detection on a single base64 webcam frame."""
    # Create or reuse inspection
    inspection_id = body.inspection_id
    if not inspection_id:
        inspection = Inspection(inspection_type="camera", status="processing")
        db.add(inspection)
        await db.flush()
        inspection_id = inspection.id
    else:
        result = await db.execute(select(Inspection).where(Inspection.id == inspection_id))
        inspection = result.scalar_one_or_none()
        if not inspection:
            raise HTTPException(404, "Inspection not found")

    # Run detection on frame
    try:
        detections = detect_frame(body.frame)
    except Exception as e:
        raise HTTPException(500, f"Frame detection failed: {str(e)}")

    anomaly_count = sum(1 for d in detections if d["is_anomaly"])

    # Save detections
    for det in detections:
        db_det = Detection(
            inspection_id=inspection_id,
            class_name=det["class_name"],
            confidence=det["confidence"],
            is_anomaly=det["is_anomaly"],
            bbox_x1=det["bbox_x1"],
            bbox_y1=det["bbox_y1"],
            bbox_x2=det["bbox_x2"],
            bbox_y2=det["bbox_y2"],
        )
        db.add(db_det)

    inspection.total_anomalies = (inspection.total_anomalies or 0) + anomaly_count
    await db.flush()

    return DetectResponse(
        inspection_id=inspection_id,
        total_detections=len(detections),
        anomaly_count=anomaly_count,
        detections=[DetectionBase(**d) for d in detections],
    )
