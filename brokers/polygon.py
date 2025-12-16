from __future__ import annotations

from typing import Dict

from brokers.base import Broker, OrderRequest, OrderResult


class PolygonBroker:
    """
    Polygon (EVM) broker adapter — API skeleton only.

    This stub shows how an EVM-based execution layer would integrate
    using Web3.py and smart contracts (DEX routers, AMMs, etc.).
    No private keys or transactions are used here.
    """

    def __init__(self):
        # Placeholder for future Web3 and wallet setup
        # Example:
        #   self.web3 = Web3(HTTPProvider(POLYGON_RPC_URL))
        #   self.account = self.web3.eth.account.from_key(PRIVATE_KEY)
        self._last_prices: Dict[str, float] = {}

    def get_last_price(self, symbol: str) -> float:
        """
        Return cached price for a token pair.

        In production, this could come from:
          - Chainlink price feeds
          - DEX quote functions (Uniswap/Sushi/QuickSwap)
        """
        return self._last_prices.get(symbol, 0.0)

    def update_last_price(self, symbol: str, price: float) -> None:
        """
        Update local price cache.
        In production, driven by oracle feeds or on-chain calls.
        """
        self._last_prices[symbol] = float(price)

    def get_balance(self) -> float:
        """
        Return native MATIC or ERC-20 token balance.

        Real implementation would call:
          - web3.eth.get_balance(...)
          - ERC-20 balanceOf(...)
        """
        raise NotImplementedError(
            "PolygonBroker.get_balance() not implemented (API skeleton only)"
        )

    def place_order(self, req: OrderRequest) -> OrderResult:
        """
        Execute a trade via a Polygon DEX.

        Real implementation would:
          - Approve token spending
          - Call a router contract (e.g., QuickSwap)
          - Sign and send the transaction
        """
        raise NotImplementedError(
            "PolygonBroker.place_order() not implemented (API skeleton only)"
        )
