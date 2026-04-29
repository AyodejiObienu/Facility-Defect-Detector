"""Pydantic schemas for request / response serialization."""

from datetime import datetime
from pydantic import BaseModel


# ── Detection ────────────────────────────────────────────────────────

class DetectionBase(BaseModel):
    class_name: str
    confidence: float
    is_anomaly: bool
    bbox_x1: float
    bbox_y1: float
    bbox_x2: float
    bbox_y2: float
    frame_number: int | None = None


class DetectionResponse(DetectionBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Media File ───────────────────────────────────────────────────────

class MediaFileResponse(BaseModel):
    id: str
    file_name: str
    file_type: str
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Inspection ───────────────────────────────────────────────────────

class InspectionSummary(BaseModel):
    id: str
    inspection_type: str
    status: str
    total_anomalies: int
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class InspectionDetail(InspectionSummary):
    detections: list[DetectionResponse] = []
    media_files: list[MediaFileResponse] = []


# ── Upload Response ──────────────────────────────────────────────────

class UploadResponse(BaseModel):
    inspection_id: str
    file_id: str
    message: str


# ── Detect Response ──────────────────────────────────────────────────

class DetectResponse(BaseModel):
    inspection_id: str
    total_detections: int
    anomaly_count: int
    detections: list[DetectionBase]


class FrameDetectRequest(BaseModel):
    """Base64 encoded frame from webcam."""
    frame: str  # base64-encoded JPEG/PNG
    inspection_id: str | None = None


# ── Stats ────────────────────────────────────────────────────────────

class StatsResponse(BaseModel):
    total_inspections: int
    total_anomalies: int
    inspections_today: int
    anomaly_rate: float  # percentage
