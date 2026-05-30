from pydantic_settings import BaseSettings
from pydantic import SecretStr, Field
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    amadeus_client_id: SecretStr = Field(..., env="AMADEUS_CLIENT_ID")
    amadeus_client_secret: SecretStr = Field(..., env="AMADEUS_CLIENT_SECRET")
    skyscanner_api_key: SecretStr = Field(..., env="SKYSCANNER_API_KEY")
    currency_api_key: Optional[SecretStr] = Field(None, env="CURRENCY_API_KEY")

    database_url: SecretStr = Field(..., env="DATABASE_URL")
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")

    jwt_secret_key: SecretStr = Field(..., env="JWT_SECRET_KEY")
    jwt_refresh_secret_key: SecretStr = Field(..., env="JWT_REFRESH_SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    encryption_key: SecretStr = Field(..., env="ENCRYPTION_KEY")

    smtp_host: Optional[str] = Field(None, env="SMTP_HOST")
    smtp_port: Optional[int] = Field(None, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(None, env="SMTP_USER")
    smtp_password: Optional[SecretStr] = Field(None, env="SMTP_PASSWORD")
    smtp_from: Optional[str] = Field(None, env="SMTP_FROM")

    cors_origins: List[str] = Field(
        ["http://localhost:3000"],
        env="CORS_ORIGINS"
    )

    rate_limit_requests: int = Field(100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(60, env="RATE_LIMIT_WINDOW")

    enable_points_tracking: bool = Field(True, env="ENABLE_POINTS_TRACKING")
    enable_price_prediction: bool = Field(True, env="ENABLE_PRICE_PREDICTION")
    enable_alerts: bool = Field(True, env="ENABLE_ALERTS")
    max_alerts_per_user: int = Field(20, env="MAX_ALERTS_PER_USER")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
