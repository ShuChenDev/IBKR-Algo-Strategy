

import requests

from app.models import Contract, Order

from pydantic import BaseModel, field_validator, model_validator
from typing import Optional

BASE_URL = "http://127.0.0.1:8000/orders"
DEFAULT_TIMEOUT = (3.05, 10)

class PlaceOrderRequest(BaseModel):
    orderID: str
    strategyID: str
    qty: float
    side: str
    orderType: str
    price: float | None = None

    # Contract fields
    secType: str
    symbol: str
    exchange: str
    currency: str
    lastTradeDateOrContractMonth: str = ""
    strike: float | None = None
    right: str = ""
    multiplier: str = ""
    localSymbol: str = ""

def place_order(order: Order):
    c = order.contract

    payload_obj = PlaceOrderRequest(
        orderID=order.orderID,
        strategyID=order.strategyID,
        qty=order.qty,
        side=order.side,
        orderType=order.orderType,

        secType=c.secType,
        symbol=c.symbol,
        exchange=c.exchange,
        currency=c.currency,

        price=order.price,
        lastTradeDateOrContractMonth=getattr(c, "lastTradeDateOrContractMonth", None),
        strike=getattr(c, "strike", None),
        right=getattr(c, "right", None),
        multiplier=getattr(c, "multiplier", None),
        localSymbol=getattr(c, "localSymbol", None),
    )

    payload = payload_obj.model_dump(exclude_none=True)

    url = f"{BASE_URL}/place_order"
    r = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
    return (r.status_code, r.json())

def cancel_order(orderID: str):
    url = f"{BASE_URL}/{orderID}"
    r = requests.delete(url, timeout=DEFAULT_TIMEOUT)
    return (r.status_code, r.json())


def get_order(orderID: str):
    url = f"{BASE_URL}/{orderID}"
    r = requests.get(url, timeout=DEFAULT_TIMEOUT)
    return (r.status_code, r.json())