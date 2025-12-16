from __future__ import annotations

import uuid
from typing import Dict

from brokers.base import Broker, OrderRequest, OrderResult


class PaperBroker:
    """
    Simulated broker for backtesting and paper trading.
    Uses in-memory balance and last price.
    """

    def __init__(self, starting_balance: float):
        self.balance = float(starting_balance)
        self.last_prices: Dict[str, float] = {}

    def set_last_price(self, symbol: str, price: float) -> None:
        """
        Update the latest market price for a symbol.
        Typically called once per tick/bar.
        """
        self.last_prices[symbol] = float(price)

    def get_last_price(self, symbol: str) -> float:
        return self.last_prices.get(symbol, 0.0)

    def get_balance(self) -> float:
        return self.balance

    def place_order(self, req: OrderRequest) -> OrderResult:
        price = self.get_last_price(req.symbol)

        if price <= 0:
            return OrderResult(
                order_id="",
                status="REJECTED",
                filled_qty=0.0,
                avg_price=0.0,
                raw={"error": "No market price available"},
            )

        cost = req.quantity * price

        if req.side == "BUY":
            if cost > self.balance:
                return OrderResult(
                    order_id="",
                    status="REJECTED",
                    filled_qty=0.0,
                    avg_price=0.0,
                    raw={"error": "Insufficient balance"},
                )
            self.balance -= cost

        elif req.side == "SELL":
            self.balance += cost

        return OrderResult(
            order_id=str(uuid.uuid4()),
            status="FILLED",
            filled_qty=req.quantity,
            avg_price=price,
            raw={"broker": "paper"},
        )
