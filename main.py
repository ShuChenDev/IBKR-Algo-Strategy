import requests
import app.models

from app.api.orders import *

contract = Contract(
  "STK",
  "TSLA",
  "SMART",
  'USD'
)
order = Order(
  orderID="253",
  strategyID="1",
  status=1,
  qty=1,
  qtyFilled=0,
  qtyUnfilled=0,
  averageCost=0,
  side="BUY",
  orderType="LMT",
  price=1,
  contract=contract,
)

print(place_order(order))

print(get_order("253"))

print(cancel_order("253"))
print(get_order("253"))


