# solana_bot/client.py

import random
import time

class SolanaClient:
    """
    Mock Solana client for demo/testing.
    Generates synthetic market values + slot numbers.
    """

    def __init__(self, config):
        self.config = config
        self.market = config.get("market_address", "SOL/USDC")
        self._price = 95.0
        self._slot = 200000000

    def get_market_data(self):
        # Simulate slot progression
        self._slot += 1

        # Simulate simple market movement
        delta = random.uniform(-0.5, 0.5)
        self._price = max(1.0, self._price + delta)

        return {
            "market": self.market,
            "slot": self._slot,
            "price": round(self._price, 3),
            "volume": random.uniform(1000, 5000),
            "timestamp": time.time(),
        }

    def execute_trade(self, action):
        print(f"[SOLANA MOCK] Executing trade: {action}")
        return True
