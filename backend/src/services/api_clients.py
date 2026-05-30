import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
from src.config import settings
from src.security import api_key_manager


class BaseAPIClient:

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _generate_cache_key(self, *args, **kwargs) -> str:
        raw = f"{self.service_name}:{json.dumps(args, sort_keys=True)}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _get_api_key(self) -> Optional[str]:
        return api_key_manager.get_api_key(self.service_name)


class AmadeusClient(BaseAPIClient):

    BASE_URL = "https://test.api.amadeus.com"

    def __init__(self):
        super().__init__("amadeus")
        self.access_token = None
        self.token_expiry = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def authenticate(self):
        client_id = settings.amadeus_client_id.get_secret_value()
        client_secret = settings.amadeus_client_secret.get_secret_value()

        response = await self.client.post(
            f"{self.BASE_URL}/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            }
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data["access_token"]
        self.token_expiry = datetime.now() + timedelta(seconds=data["expires_in"])

    async def ensure_authenticated(self):
        if not self.access_token or datetime.now() >= self.token_expiry:
            await self.authenticate()

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        max_results: int = 50,
        max_price: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        await self.ensure_authenticated()

        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "max": min(max_results, 250),
            "currencyCode": "USD",
        }

        if return_date:
            params["returnDate"] = return_date

        if max_price:
            params["maxPrice"] = max_price

        response = await self.client.get(
            f"{self.BASE_URL}/v2/shopping/flight-offers",
            params=params,
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        response.raise_for_status()

        data = response.json()
        return self._normalize_results(data.get("data", []))

    def _normalize_results(self, raw_data: List[Dict]) -> List[Dict]:
        normalized = []
        for offer in raw_data:
            try:
                itinerary = offer["itineraries"][0]
                first_segment = itinerary["segments"][0]

                price = float(offer["price"]["grandTotal"])

                normalized.append({
                    "source_api": "amadeus",
                    "origin": first_segment["departure"]["iataCode"],
                    "destination": first_segment["arrival"]["iataCode"],
                    "departure_date": first_segment["departure"]["at"],
                    "return_date": None,
                    "airline": first_segment.get("carrierCode"),
                    "flight_number": f"{first_segment.get('carrierCode')}{first_segment.get('number')}",
                    "price_amount": price,
                    "price_currency": offer["price"]["currency"],
                    "stops": len(itinerary["segments"]) - 1,
                    "cabin_class": first_segment.get("cabin", "economy"),
                    "available_seats": offer.get("numberOfBookableSeats", 0),
                    "raw_data_hash": hashlib.sha256(
                        json.dumps(offer, sort_keys=True).encode()
                    ).hexdigest()
                })
            except (KeyError, IndexError, ValueError) as e:
                logger.warning(f"Failed to normalize offer: {e}")
                continue

        return normalized


class SkyscannerClient(BaseAPIClient):

    BASE_URL = "https://partners.api.skyscanner.net/apiservices/v3"

    def __init__(self):
        super().__init__("skyscanner")

    async def create_search(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        currency: str = "USD",
    ) -> str:
        api_key = self._get_api_key()

        payload = {
            "query": {
                "market": "US",
                "locale": "en-US",
                "currency": currency,
                "queryLegs": [
                    {
                        "originPlaceId": {"iata": origin},
                        "destinationPlaceId": {"iata": destination},
                        "date": {
                            "year": int(departure_date[:4]),
                            "month": int(departure_date[5:7]),
                            "day": int(departure_date[8:10]),
                        }
                    }
                ],
                "adults": adults,
            }
        }

        if return_date:
            payload["query"]["queryLegs"].append({
                "originPlaceId": {"iata": destination},
                "destinationPlaceId": {"iata": origin},
                "date": {
                    "year": int(return_date[:4]),
                    "month": int(return_date[5:7]),
                    "day": int(return_date[8:10]),
                }
            })

        response = await self.client.post(
            f"{self.BASE_URL}/flights/live/search/create",
            json=payload,
            headers={"x-api-key": api_key}
        )
        response.raise_for_status()
        return response.json()["sessionToken"]

    async def poll_results(self, session_token: str) -> List[Dict]:
        api_key = self._get_api_key()

        response = await self.client.get(
            f"{self.BASE_URL}/flights/live/search/poll/{session_token}",
            headers={"x-api-key": api_key}
        )
        response.raise_for_status()

        data = response.json()
        results = []

        for itinerary in data.get("itineraries", []):
            try:
                if not itinerary.get("pricingOptions"):
                    continue

                price = itinerary["pricingOptions"][0]["price"]["amount"]
                leg = itinerary["legs"][0]

                results.append({
                    "source_api": "skyscanner",
                    "origin": leg["originPlaceId"],
                    "destination": leg["destinationPlaceId"],
                    "departure_date": leg["departureDateTime"],
                    "price_amount": float(price) / 1000,
                    "price_currency": "USD",
                    "stops": len(leg.get("stopPlaces", [])),
                    "airline": leg.get("carriers", {}).get("marketing", [{}])[0].get("name"),
                    "raw_data_hash": hashlib.sha256(
                        json.dumps(itinerary, sort_keys=True).encode()
                    ).hexdigest()
                })
            except (KeyError, IndexError) as e:
                logger.warning(f"Failed to parse itinerary: {e}")
                continue

        return results
