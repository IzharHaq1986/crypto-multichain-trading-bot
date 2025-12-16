# binance_bot/client.py

import random
import time

class BinanceClient:
    """
    Mock Binance client used when live API access is restricted.
    Generates simulated BTCUSDT prices and volumes.
    """

    def __init__(self, config):
        self.config = config
        self.symbol = config.get("symbol", "BTCUSDT")
        self._price = 42000.0  # starting mock price

    def get_market_data(self):
        # Simple random walk for price
        delta = random.uniform(-50, 50)
        self._price = max(1000.0, self._price + delta)
        volume = random.uniform(1, 100)

        return {
            "symbol": self.symbol,
            "price": round(self._price, 2),
            "volume": round(volume, 4),
            "timestamp": time.time(),
        }

    def execute_trade(self, action):
        print(f"[BINANCE MOCK] Executing trade: {action}")
        return True
