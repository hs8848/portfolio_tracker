from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from datetime import datetime, timezone
from enum import Enum as PyEnum

from .database import Base

class User(Base):
    """User class for the appication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    holdings = relationship("Holding", back_populates="user")


class InstrumentType(str, PyEnum):
    """Instrument type enum to hold different types of instruments. Used for classification"""
    MF = "MF"
    STOCK = "STOCK"
    BOND = "BOND"


class Instrument(Base):
    """Instrument static details class."""
    __tablename__ = "instrument"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Enum(InstrumentType), nullable=False)
    isin = Column(String, nullable=False)

    ext_id_01 = Column(String)
    ext_id_01_type = Column(String)

    amc = Column(String)
    mf_class = Column(String)
    issuer = Column(String)

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    prices = relationship("Price", back_populates="instrument")


class Holding(Base):
    """Class with users financial instruments holdings. """
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    instrument_id = Column(Integer, ForeignKey("instrument.id"), nullable=False)

    quantity = Column(Float, nullable=False)
    avg_cost_price = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="holdings")
    instrument = relationship("Instrument")


class Price(Base):
    """Class to hold instrument price details, sourced from external providers."""
    __tablename__ = "price"

    id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, ForeignKey("instrument.id"), nullable=False)

    price = Column(Float, nullable=False)
    price_date_time = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    source = Column(String, nullable=False)

    instrument = relationship("Instrument", back_populates="prices")


class PortfolioValuation(Base):
    """Class that holds the portfolio valuations for a given user on a given date."""
    __tablename__ = "portfolio_valuation"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    instrument_id = Column(Integer, ForeignKey("instrument.id"), nullable=False)

    val_date = Column(DateTime, nullable=False)
    valuation = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)

