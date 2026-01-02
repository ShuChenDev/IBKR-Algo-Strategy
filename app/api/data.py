import requests

from pydantic import BaseModel
from typing import Optional

from app.models import Contract

BASE_URL = "http://127.0.0.1:8000/data"
DEFAULT_TIMEOUT = (3.05, 10)


class DataSubscriptionRequest(BaseModel):
    strategyID: str

    # Contract fields
    secType: str
    symbol: str
    exchange: str
    currency: str
    lastTradeDateOrContractMonth: Optional[str] = None
    strike: Optional[float] = None
    right: Optional[str] = None
    multiplier: Optional[str] = None
    localSymbol: Optional[str] = None


# ----- Historical Data -----
# IMPORTANT, CSV FORMAT
def get_historical_data(contract:Contract,):
    url = f"{BASE_URL}/unsubscribe"
    r = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
    return (r.status_code, r.json())





# ----- Live Data -----
# IMPORTANT, ADD WEBSOCKET CONNECTION

def subscribe_market_data(strategyID: str, contract: Contract):
    payload_obj = DataSubscriptionRequest(
        strategyID=strategyID,
        secType=contract.secType,
        symbol=contract.symbol,
        exchange=contract.exchange,
        currency=contract.currency,

        lastTradeDateOrContractMonth=contract.lastTradeDateOrContractMonth,
        strike=contract.strike,
        right=contract.right,
        multiplier=contract.multiplier,
        localSymbol=contract.localSymbol,
    )

    payload = payload_obj.model_dump(
        exclude_none=True,
        exclude_unset=True
    )

    url = f"{BASE_URL}/unsubscribe"
    r = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
    return (r.status_code, r.json())


def unsubscribe_market_data(strategyID: str, contract: Contract):
    payload_obj = DataSubscriptionRequest(
        strategyID=strategyID,
        secType=contract.secType,
        symbol=contract.symbol,
        exchange=contract.exchange,
        currency=contract.currency,

        lastTradeDateOrContractMonth=contract.lastTradeDateOrContractMonth,
        strike=contract.strike,
        right=contract.right,
        multiplier=contract.multiplier,
        localSymbol=contract.localSymbol,
    )

    payload = payload_obj.model_dump(
        exclude_none=True,
        exclude_unset=True
    )

    url = f"{BASE_URL}/unsubscribe"
    r = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
    return (r.status_code, r.json())
