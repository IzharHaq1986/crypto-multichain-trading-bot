# polygon_bot/client.py

import random
import time

class PolygonClient:
    """
    Mock Polygon client for demo/testing.
    Produces synthetic token price + block height.
    """

    def __init__(self, config):
        self.config = config
        self.token = config.get("token_address", "MATIC")
        self._price = 1.20
        self._block = 50000000

    def get_market_data(self):
        # Simulate block progression
        self._block += 1

        # Simulate token price movement
        delta = random.uniform(-0.02, 0.02)
        self._price = max(0.01, self._price + delta)

        return {
            "token": self.token,
            "latest_block": self._block,
            "price": round(self._price, 4),
            "volume": random.uniform(500, 2000),
            "timestamp": time.time(),
        }

    def execute_trade(self, action):
        print(f"[POLYGON MOCK] Executing trade: {action}")
        return True
