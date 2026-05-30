from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base


class FlightDeal(Base):
    __tablename__ = "flight_deals"

    id = Column(Integer, primary_key=True, index=True)

    origin = Column(String(3), nullable=False, index=True)
    destination = Column(String(3), nullable=False, index=True)
    departure_date = Column(DateTime(timezone=True), nullable=False, index=True)
    return_date = Column(DateTime(timezone=True), nullable=True)
    airline = Column(String(100), nullable=True)
    flight_number = Column(String(50), nullable=True)

    price_amount = Column(Float, nullable=False)
    price_currency = Column(String(3), default="USD")
    original_price = Column(Float, nullable=True)
    discount_percentage = Column(Float, nullable=True)

    deal_type = Column(String(50), nullable=True)
    deal_quality = Column(String(20), nullable=True)

    points_program = Column(String(100), nullable=True)
    points_required = Column(Integer, nullable=True)
    points_conversion_rate = Column(Float, nullable=True)

    booking_link = Column(String(2000), nullable=True)
    deep_link = Column(String(2000), nullable=True)

    stops = Column(Integer, default=0)
    cabin_class = Column(String(50), default="economy")
    available_seats = Column(Integer, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    source_api = Column(String(50), nullable=False)
    raw_data_hash = Column(String(64), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "origin": self.origin,
            "destination": self.destination,
            "departure_date": self.departure_date.isoformat(),
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "airline": self.airline,
            "price_amount": self.price_amount,
            "price_currency": self.price_currency,
            "discount_percentage": self.discount_percentage,
            "deal_quality": self.deal_quality,
            "points_program": self.points_program,
            "points_required": self.points_required,
            "points_conversion_rate": self.points_conversion_rate,
            "stops": self.stops,
            "cabin_class": self.cabin_class,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=True)
    max_price = Column(Float, nullable=True)
    date_range_start = Column(DateTime(timezone=True), nullable=True)
    date_range_end = Column(DateTime(timezone=True), nullable=True)

    preferred_airlines = Column(String(500), nullable=True)
    max_stops = Column(Integer, default=2)
    cabin_classes = Column(String(200), nullable=True)
    deal_quality_minimum = Column(String(20), default="good")

    is_active = Column(Boolean, default=True)
    notify_email = Column(Boolean, default=True)
    notify_push = Column(Boolean, default=False)
    last_triggered = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="alerts")

    def to_dict(self):
        return {
            "id": self.id,
            "origin": self.origin,
            "destination": self.destination,
            "max_price": self.max_price,
            "date_range_start": self.date_range_start.isoformat() if self.date_range_start else None,
            "date_range_end": self.date_range_end.isoformat() if self.date_range_end else None,
            "is_active": self.is_active,
            "deal_quality_minimum": self.deal_quality_minimum,
        }


class Search(Base):
    __tablename__ = "searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    search_query = Column(JSON, nullable=False)
    results_count = Column(Integer, default=0)
    best_price_found = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="searches")


class SavedFlight(Base):
    __tablename__ = "saved_flights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    flight_data = Column(JSON, nullable=False)
    notes = Column(String(1000), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="saved_flights")
