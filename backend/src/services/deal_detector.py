from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.models.flight import FlightDeal


class DealDetector:

    THRESHOLDS = {
        "domestic": {
            "good": 0.15,
            "great": 0.30,
            "exceptional": 0.50
        },
        "international": {
            "good": 0.20,
            "great": 0.35,
            "exceptional": 0.55
        }
    }

    POINTS_VALUATIONS = {
        "amex_mr": 2.0,
        "chase_ur": 2.0,
        "citi_typ": 1.8,
        "capital_one": 1.5,
        "aa_advantage": 1.5,
        "delta_skymiles": 1.3,
        "united_mileageplus": 1.4,
        "southwest_rapid_rewards": 1.5,
        "marriott_bonvoy": 0.8,
        "hilton_honors": 0.6,
    }

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def classify_deal(
        self,
        origin: str,
        destination: str,
        price: float,
        departure_date: datetime,
        airline: Optional[str] = None,
    ) -> Dict[str, Any]:
        is_domestic = self.is_domestic(origin, destination)
        route_type = "domestic" if is_domestic else "international"

        historical_avg = await self._get_historical_average(
            origin, destination, departure_date
        )

        if historical_avg is None:
            return self._heuristic_classification(
                origin, destination, price, route_type, departure_date
            )

        discount = (historical_avg - price) / historical_avg
        thresholds = self.THRESHOLDS[route_type]

        quality = None
        if discount >= thresholds["exceptional"]:
            quality = "exceptional"
        elif discount >= thresholds["great"]:
            quality = "great"
        elif discount >= thresholds["good"]:
            quality = "good"

        return {
            "is_deal": discount >= thresholds["good"],
            "deal_quality": quality,
            "discount_percentage": round(discount * 100, 2),
            "historical_average": historical_avg,
            "savings": historical_avg - price,
            "route_type": route_type,
        }

    async def calculate_points_value(
        self,
        price: float,
        points_program: str,
        points_required: Optional[int] = None,
    ) -> Dict[str, Any]:
        valuation = self.POINTS_VALUATIONS.get(points_program.lower(), 1.0)

        if points_required:
            cpp = (price * 100) / points_required
            is_good_points_deal = cpp > valuation
        else:
            estimated_points = (price * 100) / valuation
            cpp = valuation
            is_good_points_deal = None

        return {
            "points_program": points_program,
            "points_required": points_required or estimated_points,
            "cents_per_point": round(cpp, 2),
            "valuation_baseline": valuation,
            "is_good_points_deal": is_good_points_deal,
            "cash_vs_points_recommendation": "points" if is_good_points_deal else "cash"
        }

    def detect_error_fares(
        self,
        flights: List[Dict],
        route_type: str,
    ) -> List[Dict]:
        error_fares = []

        for flight in flights:
            price = flight.get("price_amount", 0)
            if price <= 0:
                continue

            indicators = []

            if route_type == "international" and price < 100:
                indicators.append("suspiciously_low_international")
            elif route_type == "domestic" and price < 20:
                indicators.append("suspiciously_low_domestic")

            if flight.get("cabin_class", "").lower() in ["business", "first"] and price < 500:
                indicators.append("premium_cabin_mispricing")

            if indicators:
                flight["error_fare_indicators"] = indicators
                flight["deal_type"] = "error_fare"
                flight["deal_quality"] = "exceptional"
                error_fares.append(flight)

        return error_fares

    async def _get_historical_average(
        self,
        origin: str,
        destination: str,
        date: datetime,
    ) -> Optional[float]:
        date_start = date - timedelta(days=7)
        date_end = date + timedelta(days=7)

        query = select(func.avg(FlightDeal.price_amount)).where(
            FlightDeal.origin == origin,
            FlightDeal.destination == destination,
            FlightDeal.departure_date.between(date_start, date_end),
            FlightDeal.created_at >= datetime.now() - timedelta(days=90)
        )

        result = await self.db.execute(query)
        avg_price = result.scalar()
        return float(avg_price) if avg_price else None

    def is_domestic(self, origin: str, destination: str) -> bool:
        us_airports = {"JFK", "LAX", "ORD", "DFW", "DEN", "SFO", "MIA", "ATL", "BOS", "SEA", "PHX", "MCO"}
        eu_airports = {"LHR", "CDG", "FRA", "AMS", "MAD", "BCN", "FCO", "MUC", "ZRH", "VIE"}

        for region in [us_airports, eu_airports]:
            if origin in region and destination in region:
                return True
        return False

    def _heuristic_classification(
        self,
        origin: str,
        destination: str,
        price: float,
        route_type: str,
        date: datetime,
    ) -> Dict[str, Any]:
        if route_type == "domestic":
            typical_price_range = (150, 500)
        else:
            typical_price_range = (400, 2000)

        discount = 0
        if price < typical_price_range[0]:
            discount = (typical_price_range[0] - price) / typical_price_range[0]

        quality = None
        thresholds = self.THRESHOLDS[route_type]
        if discount >= thresholds["exceptional"]:
            quality = "exceptional"
        elif discount >= thresholds["great"]:
            quality = "great"
        elif discount >= thresholds["good"]:
            quality = "good"

        return {
            "is_deal": quality is not None,
            "deal_quality": quality,
            "discount_percentage": round(discount * 100, 2),
            "historical_average": typical_price_range[0],
            "savings": typical_price_range[0] - price,
            "route_type": route_type,
        }
