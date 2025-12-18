import httpx
from datetime import datetime, date, timedelta
from typing import Tuple
from ..config import ALPHAVANTAGE_API_KEY

BASE_URL = "https://www.alphavantage.co/query"

def fetch_stock_price(instrument) -> Tuple[float, datetime, str]:
    if not instrument.ext_id_01:
        raise ValueError("Stock symbol missing")

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": instrument.ext_id_01,
        "apikey": ALPHAVANTAGE_API_KEY
    }

    print(params)

    response = httpx.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()

    print(response)

    try:
        data = response.json()
        quote = data.get("Global Quote")

        if not quote or "05. price" not in quote:
            raise ValueError("Invalid stock price response")
    
        price = float(quote["05. price"])
        trade_date = datetime.strptime(
            quote["07. latest trading day"], "%Y-%m-%d"
        )
    
    except (Exception) as e:
        raise Exception(f"Error retrieving stock price data for: {instrument.ext_id_01}") from e

    return price, trade_date, "ALPHAVANTAGE"

