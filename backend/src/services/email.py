from typing import Optional
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from jinja2 import Environment, FileSystemLoader
from loguru import logger
from src.config import settings

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


async def send_email(
    to: str,
    subject: str,
    template_name: str,
    context: dict,
) -> bool:
    host = settings.smtp_host
    port = settings.smtp_port
    user = settings.smtp_user
    password = settings.smtp_password
    from_addr = settings.smtp_from or user

    if not all([host, port, user, password]):
        logger.warning("SMTP not configured — skipping email to {to}")
        return False

    try:
        html = env.get_template(f"{template_name}.html").render(**context)
        text = env.get_template(f"{template_name}.txt").render(**context)

        msg = MIMEMultipart("alternative")
        msg["From"] = from_addr
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        smtp_password = password.get_secret_value() if hasattr(password, "get_secret_value") else str(password)

        await aiosmtplib.send(
            msg,
            hostname=host,
            port=port,
            username=user,
            password=smtp_password,
            start_tls=True,
        )
        logger.info(f"Email sent to {to}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False


async def send_price_alert(
    user_email: str,
    username: str,
    origin: str,
    destination: str,
    price: float,
    currency: str,
    deal_quality: str,
    discount: Optional[float] = None,
    booking_link: Optional[str] = None,
) -> bool:
    return await send_email(
        to=user_email,
        subject=f"🔥 {deal_quality.title()} deal: {origin} → {destination} for {currency} {price:.0f}",
        template_name="price_alert",
        context={
            "username": username,
            "origin": origin,
            "destination": destination,
            "price": f"{currency} {price:.0f}",
            "deal_quality": deal_quality,
            "discount": f"{discount:.0f}%" if discount else None,
            "booking_link": booking_link or "#",
        },
    )


async def send_points_alert(
    user_email: str,
    username: str,
    origin: str,
    destination: str,
    points_program: str,
    points_required: int,
    cash_price: float,
    currency: str,
    cpp: float,
) -> bool:
    return await send_email(
        to=user_email,
        subject=f"⭐ Points deal: {origin} → {destination} — {points_required:,} {points_program} pts",
        template_name="points_alert",
        context={
            "username": username,
            "origin": origin,
            "destination": destination,
            "points_program": points_program,
            "points_required": f"{points_required:,}",
            "cash_price": f"{currency} {cash_price:.0f}",
            "cpp": f"{cpp:.2f}",
        },
    )


async def send_password_reset(
    user_email: str,
    username: str,
    reset_link: str,
) -> bool:
    return await send_email(
        to=user_email,
        subject="Password Reset — FlightScanner",
        template_name="password_reset",
        context={
            "username": username,
            "reset_link": reset_link,
        },
    )
