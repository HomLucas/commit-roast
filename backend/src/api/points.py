from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.services.auth import get_current_user, get_current_premium_user
from src.models.user import User
from src.services.deal_detector import DealDetector

router = APIRouter()


@router.get("/valuation")
async def get_points_valuation(
    program: str = Query(..., description="Points program code (e.g., amex_mr, chase_ur)"),
    current_user: User = Depends(get_current_user),
):
    valuations = DealDetector.POINTS_VALUATIONS
    if program.lower() not in valuations:
        return {
            "program": program,
            "valuation_cents_per_point": 1.0,
            "note": "Unknown program, using default valuation",
        }
    return {
        "program": program.lower(),
        "valuation_cents_per_point": valuations[program.lower()],
    }


@router.get("/all-valuations")
async def get_all_valuations(
    current_user: User = Depends(get_current_premium_user),
):
    return {
        "valuations": DealDetector.POINTS_VALUATIONS,
        "note": "Values are in cents per point",
    }


@router.post("/analyze")
async def analyze_points_deal(
    price: float = Query(..., ge=0),
    points_program: str = Query(...),
    points_required: Optional[int] = Query(None, ge=0),
    current_user: User = Depends(get_current_user),
):
    detector = DealDetector(None)
    result = await detector.calculate_points_value(
        price=price,
        points_program=points_program,
        points_required=points_required,
    )
    return result
