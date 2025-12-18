from datetime import datetime, timedelta, timezone
from app.models import Price, Instrument
from app.database import SessionLocal
from .mf_nav_service import fetch_mf_nav

import random

# def fetch_mf_nav(instrument):
#     price = round(random.uniform(10, 500), 2)
#     price_date = datetime.now(timezone.utc) - timedelta(days=1)
#     return price, price_date, "MF_API"

def fetch_stock_price(instrument):
    price = round(random.uniform(100, 5000), 2)
    price_date = datetime.now(timezone.utc)
    return price, price_date, "STOCK_API"

def fetch_bond_price(instrument):
    price = round(random.uniform(80, 120), 2)
    price_date = datetime.now(timezone.utc)
    return price, price_date, "BOND_API"


def refresh_prices():
    db = SessionLocal()
    instruments = db.query(Instrument).all()

    for inst in instruments:
        if inst.type == "MF":
            price, dt, src = fetch_mf_nav(inst)
        elif inst.type == "STOCK":
            price, dt, src = fetch_stock_price(inst)
        else:
            price, dt, src = fetch_bond_price(inst)

        p = Price(
            instrument_id=inst.id,
            price=price,
            price_date_time=dt,
            source=src
        )
        db.add(p)

    db.commit()
    db.close()
