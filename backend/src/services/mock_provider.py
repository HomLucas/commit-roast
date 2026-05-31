"""
Mock flight data provider for development/demo when no API keys are available
"""
import hashlib
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from loguru import logger


AIRLINES = ["Delta", "United", "American", "Southwest", "JetBlue", "Alaska", "Spirit", "Frontier"]
CABIN_CLASSES = ["economy", "premium_economy", "business"]

ROUTES = {
    "domestic": [
        ("LAX", "JFK"), ("JFK", "LAX"), ("ORD", "MIA"), ("ATL", "DFW"),
        ("SEA", "DEN"), ("BOS", "ORD"), ("MCO", "PHX"), ("SFO", "LAS"),
        ("LAX", "ORD"), ("JFK", "ATL"), ("DFW", "SEA"), ("MIA", "BOS"),
    ],
    "international": [
        ("JFK", "LHR"), ("LHR", "JFK"), ("LAX", "NRT"), ("ORD", "CDG"),
        ("SFO", "HND"), ("MIA", "GRU"), ("ATL", "AMS"), ("BOS", "DUB"),
        ("SEA", "ICN"), ("DFW", "FRA"), ("JFK", "HKG"), ("LAX", "SYD"),
    ],
}


def generate_mock_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = None,
    count: int = 15,
) -> List[Dict[str, Any]]:
    is_domestic = _check_domestic(origin, destination)
    price_range = (150, 500) if is_domestic else (400, 1800)
    results = []

    for i in range(count):
        airline = random.choice(AIRLINES)
        price = round(random.uniform(price_range[0], price_range[1]), 2)
        discount = round(random.uniform(0, 40), 1)
        deal_quality = None
        if discount >= 35:
            deal_quality = "exceptional"
        elif discount >= 20:
            deal_quality = "great"
        elif discount >= 10:
            deal_quality = "good"

        flight = {
            "source_api": "mock",
            "origin": origin,
            "destination": destination,
            "departure_date": f"{departure_date}T{random.randint(6, 22):02d}:{random.randint(0, 59):02d}:00",
            "return_date": f"{return_date}T{random.randint(6, 22):02d}:{random.randint(0, 59):02d}:00" if return_date else None,
            "airline": airline,
            "flight_number": f"{airline[:2].upper()}{random.randint(100, 999)}",
            "price_amount": price,
            "price_currency": "USD",
            "original_price": round(price / (1 - discount / 100), 2) if discount > 0 else price,
            "discount_percentage": discount,
            "stops": random.choices([0, 0, 0, 1, 1, 2], weights=[40, 0, 0, 30, 0, 30])[0] if not is_domestic else random.choices([0, 0, 0, 1], weights=[60, 0, 0, 40])[0],
            "cabin_class": random.choice(CABIN_CLASSES),
            "available_seats": random.randint(1, 9),
            "is_deal": deal_quality is not None,
            "deal_quality": deal_quality,
            "deal_type": "error_fare" if deal_quality == "exceptional" and discount > 45 else "sale",
            "route_type": "domestic" if is_domestic else "international",
            "savings": round(price * discount / 100, 2) if discount > 0 else 0,
            "historical_average": price_range[0],
        }
        results.append(flight)

    results.sort(key=lambda x: x["discount_percentage"], reverse=True)
    logger.info(f"Generated {len(results)} mock flights for {origin}→{destination}")
    return results


def _check_domestic(origin: str, destination: str) -> bool:
    us = {"LAX", "JFK", "ORD", "DFW", "DEN", "SFO", "MIA", "ATL", "BOS", "SEA", "PHX", "MCO", "LAS"}
    return origin in us and destination in us
