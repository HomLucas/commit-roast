from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger
from src.config import settings
from src.database import init_db, close_db

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Flight Scanner API")
    await init_db()

    required_keys = [
        "amadeus_client_id",
        "amadeus_client_secret",
    ]
    for key in required_keys:
        if not getattr(settings, key, None):
            logger.warning(f"Missing API key: {key}")

    yield

    logger.info("Shutting down Flight Scanner API")
    await close_db()


app = FastAPI(
    title="Flight Scanner API",
    description="Privacy-focused flight deal scanner with points tracking",
    version="0.1.0",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

allowed_hosts = ["*"] if settings.debug else ["localhost", "127.0.0.1", "0.0.0.0"]
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts,
)


@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    return {
        "service": "Flight Scanner API",
        "version": "0.1.0",
        "status": "operational",
        "environment": settings.environment,
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
    }


from src.api import auth, flights, alerts, users, points

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(flights.router, prefix="/api/flights", tags=["Flights"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(points.router, prefix="/api/points", tags=["Points"])
