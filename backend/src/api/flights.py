from typing import Optional, List
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from loguru import logger
from src.database import get_db
from src.services.auth import get_current_user
from src.services.api_clients import AmadeusClient, SkyscannerClient
from src.services.deal_detector import DealDetector
from src.models.user import User
from src.models.flight import FlightDeal
from src.schemas.flight import (
    FlightSearchRequest,
    FlightSearchResponse,
    FlightDealResponse,
    DealAnalysisResponse,
)
from sqlalchemy import select, and_

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/search", response_model=FlightSearchResponse)
@limiter.limit("30/minute")
async def search_flights(
    request: Request,
    search_query: FlightSearchRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        amadeus = AmadeusClient()
        skyscanner = SkyscannerClient()
        deal_detector = DealDetector(db)

        all_results = []
        api_errors = []

        try:
            async with amadeus:
                amadeus_results = await amadeus.search_flights(
                    origin=search_query.origin,
                    destination=search_query.destination,
                    departure_date=search_query.departure_date.isoformat(),
                    return_date=search_query.return_date.isoformat() if search_query.return_date else None,
                    adults=search_query.passengers,
                    max_results=search_query.limit or 50,
                    max_price=search_query.max_price,
                )
                all_results.extend(amadeus_results)
        except Exception as e:
            api_errors.append(f"Amadeus: {str(e)}")
            logger.error(f"Amadeus API error: {e}")

        if not all_results and search_query.include_alternative_sources:
            try:
                async with skyscanner:
                    session_token = await skyscanner.create_search(
                        origin=search_query.origin,
                        destination=search_query.destination,
                        departure_date=search_query.departure_date.isoformat(),
                        return_date=search_query.return_date.isoformat() if search_query.return_date else None,
                        adults=search_query.passengers,
                    )
                    skyscanner_results = await skyscanner.poll_results(session_token)
                    all_results.extend(skyscanner_results)
            except Exception as e:
                api_errors.append(f"Skyscanner: {str(e)}")
                logger.error(f"Skyscanner API error: {e}")

        if not all_results:
            raise HTTPException(
                status_code=503,
                detail=f"No results available. Errors: {api_errors}"
            )

        analyzed_results = []
        for flight in all_results:
            deal_analysis = await deal_detector.classify_deal(
                origin=flight["origin"],
                destination=flight["destination"],
                price=flight["price_amount"],
                departure_date=datetime.fromisoformat(flight["departure_date"]),
                airline=flight.get("airline"),
            )

            flight.update(deal_analysis)
            analyzed_results.append(flight)

        error_fares = deal_detector.detect_error_fares(
            analyzed_results,
            "domestic" if deal_detector.is_domestic(search_query.origin, search_query.destination) else "international"
        )

        quality_order = {"exceptional": 0, "great": 1, "good": 2, None: 3}
        analyzed_results.sort(key=lambda x: quality_order.get(x.get("deal_quality"), 3))

        background_tasks.add_task(
            _save_search_history,
            db=db,
            user_id=current_user.id,
            search_params=search_query.dict(),
            results_count=len(analyzed_results),
            best_price=analyzed_results[0]["price_amount"] if analyzed_results else None,
        )

        return FlightSearchResponse(
            query=search_query,
            total_results=len(analyzed_results),
            deals_found=sum(1 for r in analyzed_results if r.get("is_deal")),
            error_fares=len(error_fares),
            results=[FlightDealResponse(**r) for r in analyzed_results[:search_query.limit or 50]],
            api_errors=api_errors if api_errors else None,
            search_timestamp=datetime.utcnow(),
        )

    except Exception as e:
        logger.exception("Flight search failed")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/deals/{origin}/{destination}", response_model=DealAnalysisResponse)
@limiter.limit("20/minute")
async def get_route_deals(
    request: Request,
    origin: str,
    destination: str,
    date_start: Optional[date] = None,
    date_end: Optional[date] = None,
    deal_quality: Optional[str] = Query(None, regex="^(good|great|exceptional)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(FlightDeal).where(
        and_(
            FlightDeal.origin == origin.upper(),
            FlightDeal.destination == destination.upper(),
        )
    )

    if date_start:
        query = query.where(FlightDeal.departure_date >= date_start)
    if date_end:
        query = query.where(FlightDeal.departure_date <= date_end)
    if deal_quality:
        query = query.where(FlightDeal.deal_quality == deal_quality)

    query = query.order_by(FlightDeal.price_amount.asc()).limit(100)

    result = await db.execute(query)
    deals = result.scalars().all()

    return DealAnalysisResponse(
        route=f"{origin}-{destination}",
        total_deals=len(deals),
        best_price=min(d.price_amount for d in deals) if deals else None,
        deals=[FlightDealResponse.from_orm(d) for d in deals],
    )


async def _save_search_history(
    db: AsyncSession,
    user_id: int,
    search_params: dict,
    results_count: int,
    best_price: Optional[float] = None,
):
    from src.models.flight import Search

    search_record = Search(
        user_id=user_id,
        search_query=search_params,
        results_count=results_count,
        best_price_found=best_price,
    )

    db.add(search_record)
    await db.commit()
