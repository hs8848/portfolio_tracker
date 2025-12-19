from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, date

from app.models import User, PortfolioValuation, Instrument

def get_total_on_date(db, user_id, val_date):
    return (
        db.query(func.sum(PortfolioValuation.valuation))
        .filter(
            PortfolioValuation.user_id == user_id,
            func.date(PortfolioValuation.val_date) == val_date
        )
        .scalar() or 0
    )

def get_total_by_inst_type(db, user_id, val_date):
    
    print(f"Inside get_total_by_inst_type function with user_id={user_id} and val_date={val_date}")
    
    rows = (
        db.query(
            Instrument.type,
            func.sum(PortfolioValuation.valuation).label("total_value")
        )
        .join(
            Instrument,
            PortfolioValuation.instrument_id == Instrument.id
        )
        .filter(
            PortfolioValuation.user_id == user_id,
            func.date(PortfolioValuation.val_date) == val_date
        )
        .group_by(Instrument.type)
        .all()
    )

    inst_type_val_set = {}

    print(f"Inside get_total_by_inst_type function {len(rows)}")

    for r in rows:
        # inst_type_val_set.append({
        #     "inst_type": r.type,
        #     "total_value": round(r.total_value, 2)
        # })
        inst_type_val_set[r.type] = round(r.total_value, 2)
        print(f"Inst Type: {r.type}, Total Value: {r.total_value}")

    return inst_type_val_set


def get_total_by_mf_class(db, user_id, val_date):
    rows = (
        db.query(
            Instrument.mf_class,
            func.sum(PortfolioValuation.valuation).label("total_value")
        )
        .join(
            Instrument,
            PortfolioValuation.instrument_id == Instrument.id
        )
        .filter(
            PortfolioValuation.user_id == user_id,
            func.date(PortfolioValuation.val_date) == val_date,
            Instrument.type == 'MF'
        )
        .group_by(Instrument.mf_class)
        .all()
    )

    mf_class_val_set = {}

    for r in rows:
        # mf_class_val_set.append({
        #     "mf_class": r.mf_class,
        #     "total_value": round(r.total_value, 2)
        # })
        mf_class_val_set[r.mf_class] = round(r.total_value, 2)
        print(f"MF Class: {r.mf_class}, Total Value: {r.total_value}")

    return mf_class_val_set


def get_total_by_mf_amc(db, user_id, val_date):
    rows = (
        db.query(
            Instrument.amc,
            func.sum(PortfolioValuation.valuation).label("total_value")
        )
        .join(
            Instrument,
            PortfolioValuation.instrument_id == Instrument.id
        )
        .filter(
            PortfolioValuation.user_id == user_id,
            func.date(PortfolioValuation.val_date) == val_date,
            Instrument.type == 'MF'
        )
        .group_by(Instrument.amc)
        .all()
    )

    mf_amc_val_set = {}

    for r in rows:
        # mf_amc_val_set.append({
        #     "mf_amc": r.amc,
        #     "total_value": round(r.total_value, 2)
        # })
        mf_amc_val_set[r.amc] = round(r.total_value, 2)

    return mf_amc_val_set