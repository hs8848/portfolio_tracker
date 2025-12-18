from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time
import pytz

from services.valuation_service import run_eod_valuation

IST = pytz.timezone("Asia/Kolkata")

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=IST)

    scheduler.add_job(
        func=lambda: run_eod_valuation(datetime.now(IST)),
        trigger="cron",
        hour=23,
        minute=0
    )

    scheduler.start()

def shutdown_scheduler():
    # Write code later
    return True
