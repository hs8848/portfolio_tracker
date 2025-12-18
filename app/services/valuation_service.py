from sqlalchemy import desc, func
from datetime import datetime, date
from app.models import Price, User, Holding, PortfolioValuation
from app.database import SessionLocal

def get_latest_price(db, instrument_id: int, as_of: datetime):
    """Helper function to get the latest price for an instrument as of a given date."""
    return (
        db.query(Price)
        .filter(
            Price.instrument_id == instrument_id,
            Price.price_date_time <= as_of
        )
        .order_by(desc(Price.price_date_time))
        .first()
    )


def valuation_exists_for_date(db, user_id: int, instrument_id: int, val_date: date) -> bool:
    """Helper function to check if the valuation for a user/instrument/date already exists."""
    
    existing = db.query(PortfolioValuation).filter(
                    PortfolioValuation.user_id == user_id,
                    PortfolioValuation.instrument_id == instrument_id,
                    func.date(PortfolioValuation.val_date) == val_date
                ).first()
    return (existing is not None)


def run_eod_valuation(valuation_dt: datetime):
    """Main function to generate end-of-day portfolio valuations for all users."""
    
    db = SessionLocal()

    users = db.query(User).all()

    for user in users:
        holdings = (
            db.query(Holding)
            .filter(Holding.user_id == user.id)
            .all()
        )

        for h in holdings:
            price_rec = get_latest_price(db, h.instrument_id, valuation_dt)

            if not price_rec:
                print(f"No price for instrument {h.instrument_id} as of {valuation_dt}")
                continue

            value = h.quantity * price_rec.price

            if valuation_exists_for_date(db, user.id, h.instrument_id, valuation_dt.date()):
                print(f"Valuation exists for user {user.name}, for instrument: {h.instrument_id} for date {valuation_dt.date()})). Skipping.")
                continue  # idempotent
            else:
                db.add(
                    PortfolioValuation(
                        user_id=user.id,
                        instrument_id=h.instrument_id,
                        val_date=valuation_dt.date(),
                        valuation=value
                    )
            )

    db.commit()
    db.close()

