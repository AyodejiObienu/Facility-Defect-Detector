"""Results router — list and view inspection results and stats."""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Inspection, Detection
from ..schemas import InspectionSummary, InspectionDetail, StatsResponse

router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("", response_model=list[InspectionSummary])
async def list_inspections(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List all inspections, newest first."""
    result = await db.execute(
        select(Inspection)
        .order_by(Inspection.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    inspections = result.scalars().all()
    return [InspectionSummary.model_validate(i) for i in inspections]


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics."""
    # Total inspections
    total_result = await db.execute(select(func.count(Inspection.id)))
    total_inspections = total_result.scalar() or 0

    # Total anomalies
    anomaly_result = await db.execute(select(func.sum(Inspection.total_anomalies)))
    total_anomalies = anomaly_result.scalar() or 0

    # Inspections today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.count(Inspection.id)).where(Inspection.created_at >= today_start)
    )
    inspections_today = today_result.scalar() or 0

    # Anomaly rate
    anomaly_rate = 0.0
    if total_inspections > 0:
        has_anomaly_result = await db.execute(
            select(func.count(Inspection.id)).where(Inspection.total_anomalies > 0)
        )
        anomaly_inspections = has_anomaly_result.scalar() or 0
        anomaly_rate = round((anomaly_inspections / total_inspections) * 100, 1)

    return StatsResponse(
        total_inspections=total_inspections,
        total_anomalies=total_anomalies,
        inspections_today=inspections_today,
        anomaly_rate=anomaly_rate,
    )


@router.get("/{inspection_id}", response_model=InspectionDetail)
async def get_inspection(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed results for a single inspection."""
    result = await db.execute(
        select(Inspection)
        .options(
            selectinload(Inspection.detections),
            selectinload(Inspection.media_files),
        )
        .where(Inspection.id == inspection_id)
    )
    inspection = result.scalar_one_or_none()

    if not inspection:
        raise HTTPException(404, "Inspection not found")

    return InspectionDetail.model_validate(inspection)
