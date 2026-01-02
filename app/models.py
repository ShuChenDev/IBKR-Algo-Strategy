from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class Contract:
    secType: str
    symbol: str
    exchange: str
    currency: str
    lastTradeDateOrContractMonth: str = ""
    strike: float | None = None
    right: str = ""
    multiplier: str = ""
    localSymbol: str = ""

    def __post_init__(self):
        object.__setattr__(
            self, "secType", (self.secType or "").strip().upper())
        object.__setattr__(self, "symbol", (self.symbol or "").strip().upper())
        object.__setattr__(
            self, "exchange", (self.exchange or "").strip().upper())
        object.__setattr__(
            self, "currency", (self.currency or "").strip().upper())

        object.__setattr__(self, "lastTradeDateOrContractMonth",
                           (self.lastTradeDateOrContractMonth or "").strip())

        object.__setattr__(self, "right", (self.right or "").strip().upper())
        object.__setattr__(self, "multiplier", (self.multiplier or "").strip())
        object.__setattr__(self, "localSymbol",
                           (self.localSymbol or "").strip().upper())

        self.validate_contract()

    def validate_contract(self):
        if self.secType not in {"STK", "OPT", "FUT"}:
            raise ValueError(f"Invalid secType: {self.secType}")

        if not self.symbol:
            raise ValueError("Symbol is required")
        if not self.exchange:
            raise ValueError("Exchange is required")
        if not self.currency:
            raise ValueError("Currency is required")

        # Helper: treat "" or None as empty
        def _has_text(x: str) -> bool:
            return bool(x and x.strip())

        if self.secType == "STK":
            # Stocks should not include derivative-specific fields
            if _has_text(self.lastTradeDateOrContractMonth):
                raise ValueError(
                    "STK must not have lastTradeDateOrContractMonth")
            if self.strike is not None:
                raise ValueError("STK must not have strike")
            if _has_text(self.right):
                raise ValueError("STK must not have right")
            if _has_text(self.multiplier):
                raise ValueError("STK must not have multiplier")
            if _has_text(self.localSymbol):
                raise ValueError("STK must not have localSymbol")

        elif self.secType == "OPT":
            # Required: expiry YYYYMMDD, strike, right
            if (not self.lastTradeDateOrContractMonth
                or len(self.lastTradeDateOrContractMonth) != 8
                    or not self.lastTradeDateOrContractMonth.isnumeric()):
                raise ValueError(
                    "OPT requires lastTradeDateOrContractMonth (YYYYMMDD)")

            if self.strike is None:
                raise ValueError("OPT requires strike")

            if self.right not in {"C", "P"}:
                raise ValueError("OPT requires right = 'C' or 'P'")

            # Optional: multiplier/localSymbol are allowed, but if provided they must be non-whitespace (already stripped)
            # Nothing extra to forbid here.

        elif self.secType == "FUT":
            # Required: expiry YYYYMM
            if (not self.lastTradeDateOrContractMonth
                or len(self.lastTradeDateOrContractMonth) != 6
                    or not self.lastTradeDateOrContractMonth.isnumeric()):
                raise ValueError(
                    "FUT requires lastTradeDateOrContractMonth (YYYYMM)")

            # Futures should not have option-only fields
            if self.strike is not None:
                raise ValueError("FUT must not have strike")
            if _has_text(self.right):
                raise ValueError("FUT must not have right")

            # Optional: multiplier/localSymbol allowed.

    def create_contract(self) -> dict:
        contract = {
            "secType": self.secType,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "currency": self.currency,
        }
        if self.lastTradeDateOrContractMonth:
            contract["lastTradeDateOrContractMonth"] = self.lastTradeDateOrContractMonth
        if self.strike is not None:
            contract["strike"] = self.strike
        if self.right:
            contract["right"] = self.right
        if self.multiplier:
            contract["multiplier"] = self.multiplier
        if self.localSymbol:
            contract["localSymbol"] = self.localSymbol
        return contract


class Order:
    def __init__(
            self,
            orderID: str,
            strategyID: str,
            status: bool,  # True if not finished, False if finished
            qty: float,
            qtyFilled: float,
            qtyUnfilled: float,
            averageCost: float,
            side: str,
            orderType: str,
            price: float | None,
            contract: Contract,
            timePlaced: str | None = str(datetime.now(timezone.utc).isoformat())
    ):

        self.orderID: str = orderID
        self.strategyID: str = strategyID
        self.status: bool = status
        self.qty: float = float(qty) if qty is not None else None
        self.qtyFilled: float = float(
            qtyFilled) if qtyFilled is not None else None
        self.qtyUnfilled: float = float(
            qtyUnfilled) if qtyUnfilled is not None else None
        self.averageCost: float = float(
            averageCost) if averageCost is not None else None
        self.side: str = side.upper() if side else side
        self.orderType: str = orderType.upper() if orderType else orderType
        self.price: float = float(price) if price is not None else None
        self.contract: Contract = contract
        self.timePlaced = timePlaced
        self.validate_order()

    def validate_order(self):
        # --- Basic identity ---
        if not self.orderID:
            raise ValueError("orderID is required")

        if not self.strategyID:
            raise ValueError("strategyID is required")

        if not isinstance(self.contract, Contract):
            raise ValueError("contract must be a Contract object")

        # --- Quantity checks ---
        if self.qty is None or self.qty <= 0:
            raise ValueError("qty must be a positive number")

        filled = self.qtyFilled or 0.0
        unfilled = self.qtyUnfilled or (self.qty - filled)

        if filled < 0 or unfilled < 0:
            raise ValueError("qtyFilled / qtyUnfilled cannot be negative")

        if filled > self.qty:
            raise ValueError("qtyFilled cannot exceed qty")

        if abs((filled + unfilled) - self.qty) > 1e-6:
            raise ValueError("qtyFilled + qtyUnfilled must equal qty")

        # --- Side ---
        if self.side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")

        # --- Order type ---
        if self.orderType not in {"MKT", "LMT", "STP"}:
            raise ValueError("orderType must be MKT, LMT, or STP")

        # --- Price rules ---
        if self.orderType == "MKT":
            if self.price is not None:
                raise ValueError("Market orders must not have a price")

        if self.orderType in {"LMT", "STP"}:
            if self.price is None or self.price <= 0:
                raise ValueError(
                    f"{self.orderType} orders require a positive price")


class Strategy:
    def __init__(
        self,
        strategyID: str,
        name: str,
        cash: float,
        value: float = 0.0,
        position: dict[Contract, float] | None = None,
        subscribedData: list[Contract] | None = None,
        log: str = "",
    ):
        self.strategyID: str = strategyID
        self.name: str = name
        self.cash: float = float(cash)
        self.value: float = float(value)

        self.position: dict[Contract,
                            float] = position if position is not None else {}
        self.subscribedData: list[Contract] = subscribedData if subscribedData is not None else [
        ]
        self.log: str = log

    def has_position(self) -> bool:
        """
        Return True if this strategy has any open position
        """
        for qty in self.position.values():
            if qty > 0:
                return True
        return False

    def close_position(self, contract: Contract):
        """
        Close a position owned by this strategy
        """
        qty = self.position.get(contract)
        if qty is None or qty <= 0:
            return

        self.update_position(contract, -qty)

    def close_all_position(self):
        """
        Close all positions at market price
        """
        # iterate over a copy to avoid mutation issues
        for contract, qty in list(self.position.items()):
            if qty > 0:
                self.close_position(contract)

    def update_position(self, contract: Contract, qty: float):
        """
        Change the position of the strategy
        """
        current = self.position.get(contract, 0.0)
        new_qty = current + qty

        if new_qty <= 0:
            # remove empty/closed positions
            self.position.pop(contract, None)
        else:
            self.position[contract] = new_qty

    def subscribe_data(self, contract: Contract):
        """
        Subscribe to live data
        """
        if contract not in self.subscribedData:
            self.subscribedData.append(contract)

    def unsubscribe_data(self, contract: Contract):
        """
        Unsubscribe from live data
        """
        if contract in self.subscribedData:
            self.subscribedData.remove(contract)
