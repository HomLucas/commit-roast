from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from src.database import get_db
from src.models.user import User
from src.models.flight import Alert
from src.services.auth import get_current_user
from src.schemas.alerts import AlertCreate, AlertResponse, AlertUpdate
from src.config import settings

router = APIRouter()


@router.post("/", response_model=AlertResponse, status_code=201)
async def create_alert(
    alert_data: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_alerts = await db.execute(
        select(Alert).where(
            and_(Alert.user_id == current_user.id, Alert.is_active == True)
        )
    )
    active_count = len(existing_alerts.scalars().all())

    if active_count >= settings.max_alerts_per_user:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {settings.max_alerts_per_user} active alerts allowed"
        )

    alert = Alert(
        user_id=current_user.id,
        origin=alert_data.origin,
        destination=alert_data.destination,
        max_price=alert_data.max_price,
        date_range_start=alert_data.date_range_start,
        date_range_end=alert_data.date_range_end,
        preferred_airlines=alert_data.preferred_airlines,
        max_stops=alert_data.max_stops,
        cabin_classes=alert_data.cabin_classes,
        deal_quality_minimum=alert_data.deal_quality_minimum,
    )

    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    return AlertResponse.from_orm(alert)


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    include_inactive: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Alert).where(Alert.user_id == current_user.id)

    if not include_inactive:
        query = query.where(Alert.is_active == True)

    query = query.order_by(Alert.created_at.desc())

    result = await db.execute(query)
    alerts = result.scalars().all()

    return [AlertResponse.from_orm(alert) for alert in alerts]


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Alert).where(
            and_(Alert.id == alert_id, Alert.user_id == current_user.id)
        )
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return AlertResponse.from_orm(alert)


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Alert).where(
            and_(Alert.id == alert_id, Alert.user_id == current_user.id)
        )
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    for field, value in alert_update.dict(exclude_unset=True).items():
        setattr(alert, field, value)

    await db.commit()
    await db.refresh(alert)

    return AlertResponse.from_orm(alert)


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Alert).where(
            and_(Alert.id == alert_id, Alert.user_id == current_user.id)
        )
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    await db.delete(alert)
    await db.commit()

    return {"message": "Alert deleted successfully"}
