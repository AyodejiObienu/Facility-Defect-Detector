"""SQLAlchemy ORM models for inspections, detections, and media files."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inspection_type: Mapped[str] = mapped_column(String(20))  # image | video | camera
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | processing | completed | failed
    total_anomalies: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    detections: Mapped[list["Detection"]] = relationship(back_populates="inspection", cascade="all, delete-orphan")
    media_files: Mapped[list["MediaFile"]] = relationship(back_populates="inspection", cascade="all, delete-orphan")


class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inspection_id: Mapped[str] = mapped_column(ForeignKey("inspections.id", ondelete="CASCADE"))
    class_name: Mapped[str] = mapped_column(String(100))  # e.g. bunk_broken, fan_normal
    confidence: Mapped[float] = mapped_column(Float)
    is_anomaly: Mapped[bool] = mapped_column(default=False)
    bbox_x1: Mapped[float] = mapped_column(Float)
    bbox_y1: Mapped[float] = mapped_column(Float)
    bbox_x2: Mapped[float] = mapped_column(Float)
    bbox_y2: Mapped[float] = mapped_column(Float)
    frame_number: Mapped[int | None] = mapped_column(Integer, nullable=True)  # For video detections
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Relationships
    inspection: Mapped["Inspection"] = relationship(back_populates="detections")


class MediaFile(Base):
    __tablename__ = "media_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inspection_id: Mapped[str] = mapped_column(ForeignKey("inspections.id", ondelete="CASCADE"))
    file_path: Mapped[str] = mapped_column(Text)
    file_name: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(20))  # image | video
    file_size: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Relationships
    inspection: Mapped["Inspection"] = relationship(back_populates="media_files")
