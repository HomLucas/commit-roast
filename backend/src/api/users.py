from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models.user import User
from src.services.auth import get_current_user
from src.schemas.auth import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)


@router.put("/me/preferences", response_model=UserResponse)
async def update_preferences(
    preferred_currency: str = "USD",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.preferred_currency = preferred_currency
    await db.commit()
    await db.refresh(current_user)
    return UserResponse.from_orm(current_user)


@router.get("/search-history")
async def get_search_history(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from src.models.flight import Search
    result = await db.execute(
        select(Search)
        .where(Search.user_id == current_user.id)
        .order_by(Search.created_at.desc())
        .limit(limit)
    )
    searches = result.scalars().all()
    return [s.to_dict() for s in searches]


@router.get("/saved-flights")
async def get_saved_flights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from src.models.flight import SavedFlight
    result = await db.execute(
        select(SavedFlight).where(SavedFlight.user_id == current_user.id)
    )
    flights = result.scalars().all()
    return [{"id": f.id, "flight_data": f.flight_data, "notes": f.notes, "created_at": f.created_at.isoformat()} for f in flights]
