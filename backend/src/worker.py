"""
Celery background worker for alert matching and email notifications
"""
from datetime import datetime
from celery import Celery
from sqlalchemy import select, and_
from loguru import logger
from src.config import settings

celery_app = Celery(
    "flight_scanner",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "check-alerts-every-15-minutes": {
            "task": "src.worker.check_alerts",
            "schedule": 900.0,
        },
    },
)


@celery_app.task
def check_alerts():
    """Periodic task: match active alerts against newly stored flight deals"""
    import asyncio
    asyncio.run(_check_alerts_async())


async def _check_alerts_async():
    from src.database import async_session
    from src.models.flight import Alert, FlightDeal
    from src.models.user import User
    from src.services.email import send_price_alert, send_points_alert

    async with async_session() as db:
        result = await db.execute(
            select(Alert).where(Alert.is_active == True)
        )
        alerts = result.scalars().all()

        for alert in alerts:
            try:
                origins = [o.strip() for o in alert.origin.split(",")]
                dests = [d.strip() for d in alert.destination.split(",")] if alert.destination else None

                query = select(FlightDeal).where(
                    FlightDeal.origin.in_(origins),
                    FlightDeal.created_at >= (alert.last_triggered or datetime.min),
                )
                if dests:
                    query = query.where(FlightDeal.destination.in_(dests))
                if alert.max_price is not None:
                    query = query.where(FlightDeal.price_amount <= alert.max_price)
                if alert.max_stops is not None:
                    query = query.where(FlightDeal.stops <= alert.max_stops)

                deals = (await db.execute(query)).scalars().all()

                if not deals:
                    continue

                user_result = await db.execute(
                    select(User).where(User.id == alert.user_id)
                )
                user = user_result.scalar_one_or_none()
                if not user or not user.is_active:
                    continue

                for deal in deals:
                    if alert.notify_email:
                        await send_price_alert(
                            user_email=user.email,
                            username=user.username,
                            origin=deal.origin,
                            destination=deal.destination,
                            price=deal.price_amount,
                            currency=deal.price_currency,
                            deal_quality=deal.deal_quality or "good",
                            discount=deal.discount_percentage,
                        )

                        if deal.points_program and deal.points_required:
                            await send_points_alert(
                                user_email=user.email,
                                username=user.username,
                                origin=deal.origin,
                                destination=deal.destination,
                                points_program=deal.points_program,
                                points_required=deal.points_required,
                                cash_price=deal.price_amount,
                                currency=deal.price_currency,
                                cpp=deal.points_conversion_rate or 0,
                            )

                alert.last_triggered = datetime.utcnow()
                db.add(alert)

            except Exception as e:
                logger.error(f"Alert {alert.id} processing failed: {e}")

        await db.commit()
        logger.info(f"Checked {len(alerts)} alerts")
