from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field


class FlightSearchRequest(BaseModel):
    origin: str = Field(..., min_length=3, max_length=3, description="IATA origin airport code")
    destination: str = Field(..., min_length=3, max_length=3, description="IATA destination airport code")
    departure_date: date
    return_date: Optional[date] = None
    passengers: int = Field(default=1, ge=1, le=9)
    max_price: Optional[float] = Field(None, ge=0)
    limit: Optional[int] = Field(default=50, ge=1, le=250)
    include_alternative_sources: bool = Field(default=False)


class FlightDealResponse(BaseModel):
    source_api: str
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    airline: Optional[str] = None
    flight_number: Optional[str] = None
    price_amount: float
    price_currency: str = "USD"
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    stops: int = 0
    cabin_class: str = "economy"
    available_seats: Optional[int] = None
    is_deal: Optional[bool] = None
    deal_quality: Optional[str] = None
    deal_type: Optional[str] = None
    points_program: Optional[str] = None
    points_required: Optional[int] = None
    points_conversion_rate: Optional[float] = None
    historical_average: Optional[float] = None
    savings: Optional[float] = None
    route_type: Optional[str] = None


class FlightSearchResponse(BaseModel):
    query: FlightSearchRequest
    total_results: int
    deals_found: int
    error_fares: int = 0
    results: List[FlightDealResponse]
    api_errors: Optional[List[str]] = None
    search_timestamp: datetime


class DealAnalysisResponse(BaseModel):
    route: str
    total_deals: int
    best_price: Optional[float] = None
    deals: List[FlightDealResponse]
