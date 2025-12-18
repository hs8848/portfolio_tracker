from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, date

from .database import engine, SessionLocal
from .models import Base, User, Instrument, Holding, PortfolioValuation
from .schemas import UserCreate, UserLogin, Token
from .schemas import InstrumentCreate, InstrumentResponse, HoldingCreate, HoldingResponse

from .auth import hash_password, verify_password, create_access_token, get_current_user

from .services.price_service import refresh_prices
from .services.valuation_service import run_eod_valuation



#from .services.scheduler import start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Portfolio Tracker API")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        email=user.email,
        name=user.name,
        password_hash=hash_password(user.password)
    )
    
    db.add(new_user)
    db.commit()
    return {"message": "User created"}


@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email})
    return {"access_token": token}

@app.get("/me")
def read_current_user(current_user: str = Depends(get_current_user)):
    return {"email": current_user}


@app.post("/instruments", response_model=InstrumentResponse)
def create_instrument(instrument: InstrumentCreate, db: Session = Depends(get_db)):
    new_inst = Instrument(**instrument.dict())
    db.add(new_inst)
    db.commit()
    db.refresh(new_inst)
    return new_inst

@app.get("/instruments", response_model=list[InstrumentResponse])
def list_instruments(db: Session = Depends(get_db)):
    return db.query(Instrument).all()


@app.post("/holdings", response_model=dict)
def add_holding(holding: HoldingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_holding = Holding(
        user_id=current_user.id,
        instrument_id=holding.instrument_id,
        quantity=holding.quantity,
        avg_cost_price=holding.avg_cost_price
    )
    db.add(new_holding)
    db.commit()
    return {"message": "Holding added"}


@app.get("/holdings", response_model=list[HoldingResponse])
def get_holdings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    holdings = (
        db.query(Holding)
        .join(Instrument)
        .filter(Holding.user_id == current_user.id)
        .all()
    )

    return [
        {
            "id": h.id,
            "instrument_id": h.instrument.id,
            "instrument_name": h.instrument.name,
            "quantity": h.quantity,
            "avg_cost_price": h.avg_cost_price
        }
        for h in holdings
    ]

@app.post("/prices/refresh", response_model=dict)
def refresh_prices_api(current_user: User = Depends(get_current_user)):
    refresh_prices()
    return {"message": "Prices refreshed"}


@app.post("/valuation/run-eod")
def run_eod_manual(current_user: User = Depends(get_current_user)):
    run_eod_valuation(datetime.now(timezone.utc))
    return {"message": "EOD valuation executed."}


def get_total_on_date(db, user_id, val_date):
    return (
        db.query(func.sum(PortfolioValuation.valuation))
        .filter(
            PortfolioValuation.user_id == user_id,
            func.date(PortfolioValuation.val_date) == val_date
        )
        .scalar() or 0
    )


@app.get("/dashboard/summary")
def portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = date.today()

    latest_date = (
        db.query(func.max(PortfolioValuation.val_date))
        .filter(PortfolioValuation.user_id == current_user.id)
        .scalar()
    )

    if not latest_date:
        return {"total": 0}

    total = (
        db.query(func.sum(PortfolioValuation.valuation))
        .filter(
            PortfolioValuation.user_id == current_user.id,
            PortfolioValuation.val_date == latest_date
        )
        .scalar()
    )

    return {
        "as_of_date": latest_date,
        "total_value": round(total, 2)
    }


@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# Scheduler disabled during development.
# EOD valuation is triggered manually via API.
# Enable only in production.

# @app.on_event("startup")
# def startup_event():
#     start_scheduler()

# @app.on_event("shutdown")
# def shutdown_event():
#     shutdown_scheduler()