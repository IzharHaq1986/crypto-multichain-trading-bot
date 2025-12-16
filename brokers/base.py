from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, Dict, Any


@dataclass
class OrderRequest:
    symbol: str
    side: str               # "BUY" or "SELL"
    quantity: float
    order_type: str = "MARKET"
    limit_price: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class OrderResult:
    order_id: str
    status: str             # "ACCEPTED", "REJECTED", "FILLED"
    filled_qty: float
    avg_price: float
    raw: Optional[Dict[str, Any]] = None


class Broker(Protocol):
    """
    Unified broker interface.
    Real adapters (Binance/Solana/Polygon) will implement this.
    """

    def get_last_price(self, symbol: str) -> float:
        ...

    def place_order(self, req: OrderRequest) -> OrderResult:
        ...

    def get_balance(self) -> float:
        ...
