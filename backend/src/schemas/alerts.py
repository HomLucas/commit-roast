from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    origin: str = Field(..., min_length=3, description="Airport code(s), comma-separated")
    destination: Optional[str] = Field(None, description="Airport code(s), comma-separated")
    max_price: Optional[float] = Field(None, ge=0)
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    preferred_airlines: Optional[str] = None
    max_stops: int = Field(default=2, ge=0, le=4)
    cabin_classes: Optional[str] = None
    deal_quality_minimum: str = Field(default="good", pattern=r"^(good|great|exceptional)$")


class AlertUpdate(BaseModel):
    max_price: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None
    deal_quality_minimum: Optional[str] = Field(None, pattern=r"^(good|great|exceptional)$")
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    max_stops: Optional[int] = Field(None, ge=0, le=4)


class AlertResponse(BaseModel):
    id: int
    user_id: int
    origin: str
    destination: Optional[str] = None
    max_price: Optional[float] = None
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    is_active: bool
    deal_quality_minimum: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
