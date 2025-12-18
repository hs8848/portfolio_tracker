import httpx
from datetime import datetime, date, timedelta
from typing import Tuple


MFAPI_BASE_URL = "https://api.mfapi.in/mf"

def fetch_mf_nav(instrument) -> Tuple[float, datetime, str]:
    if not instrument.ext_id_01:
        raise ValueError("MF scheme code missing for instrument")

    endDate = date.today()
    startDate = endDate - timedelta(days=7)
    endDateStr = endDate.strftime("%Y-%m-%d")
    startDateStr = startDate.strftime("%Y-%m-%d")
    datePartStr = f"?startDate={startDateStr}&endDate={endDateStr}"
    
    url = f"{MFAPI_BASE_URL}/{instrument.ext_id_01}{datePartStr}"

    response = httpx.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    print(f"Fetched MF NAV data for {instrument.name}: {data}")

    latest = data["data"][0]
    nav = float(latest["nav"])

    nav_date = datetime.strptime(
        latest["date"], "%d-%m-%Y"
    )

    return nav, nav_date, "MFAPI"
