from datetime import datetime, timedelta, timezone, date
import time
from app.models import Price, Instrument
from app.database import SessionLocal
from .mf_nav_service import fetch_mf_nav
from .stock_price_service import fetch_stock_price

import random

from sqlalchemy import func

# def fetch_mf_nav(instrument):
#     price = round(random.uniform(10, 500), 2)
#     price_date = datetime.now(timezone.utc) - timedelta(days=1)
#     return price, price_date, "MF_API"

# def fetch_stock_price(instrument):
#     price = round(random.uniform(100, 5000), 2)
#     price_date = datetime.now(timezone.utc)
#     return price, price_date, "STOCK_API"

def fetch_bond_price(instrument):
    price = round(random.uniform(80, 120), 2)
    price_date = datetime.now(timezone.utc)
    return price, price_date, "BOND_API"

def price_exists_for_date(db, instrument_id: int, price_date: date, source: str) -> bool:
    
    print("Inside price_exists_for_date function")
    firstVal = db.query(Price).filter(
            Price.instrument_id == instrument_id,
            func.date(Price.price_date_time) == price_date,
            Price.source == source
        ).first()
    print("Inside price_exists_for_date function, before returning")
    return (firstVal is not None)


def refresh_prices():
    db = SessionLocal()
    instruments = db.query(Instrument).all()

    for inst in instruments:
        
        try:

            if inst.type == "MF":
                price, dt, src = fetch_mf_nav(inst)
                time.sleep(12)
            elif inst.type == "STOCK":
                price, dt, src = fetch_stock_price(inst)
                time.sleep(12)
            else:
                price, dt, src = fetch_bond_price(inst)

            print("Before new function call")
            if price_exists_for_date(db, inst.id, dt.date(), src):
                print(f"Price for {inst.name} on {dt.date()} from {src} already exists. Skipping.")
                continue

            print("After new function call")

            p = Price(
                instrument_id=inst.id,
                price=price,
                price_date_time=dt,
                source=src
            )
        except (Exception) as e:
            print(f"Error fetching price for {inst.name}: {e}")
            continue
            
        db.add(p)

    db.commit()
    db.close()
