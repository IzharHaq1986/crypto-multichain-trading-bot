from __future__ import annotations

from typing import Dict

from brokers.base import Broker, OrderRequest, OrderResult


class BinanceBroker:
    """
    Binance broker adapter (API skeleton only).

    This class defines the interface and structure needed to
    integrate with the Binance REST/WebSocket APIs later.
    No API keys or live calls are used here.
    """

    def __init__(self):
        # Placeholder for future API client initialization
        # Example: self.client = Client(api_key, api_secret)
        self._last_prices: Dict[str, float] = {}

    def get_last_price(self, symbol: str) -> float:
        """
        Return the most recent known price.
        In a real implementation, this would call:
          GET /api/v3/ticker/price
        """
        return self._last_prices.get(symbol, 0.0)

    def update_last_price(self, symbol: str, price: float) -> None:
        """
        Update price cache.
        In production, this would be driven by WebSocket streams.
        """
        self._last_prices[symbol] = float(price)

    def get_balance(self) -> float:
        """
        Return available account balance.
        Real implementation would call:
          GET /api/v3/account
        """
        raise NotImplementedError(
            "BinanceBroker.get_balance() not implemented (API skeleton only)"
        )

    def place_order(self, req: OrderRequest) -> OrderResult:
        """
        Place an order on Binance.

        Real implementation would call:
          POST /api/v3/order
        """
        raise NotImplementedError(
            "BinanceBroker.place_order() not implemented (API skeleton only)"
        )
