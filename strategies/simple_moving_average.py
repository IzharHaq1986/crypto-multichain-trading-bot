# strategies/simple_moving_average.py

from statistics import mean
from strategies.base_strategy import BaseStrategy

class SimpleMovingAverageStrategy(BaseStrategy):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.window = config.get("strategy", {}).get("sma_window", 5)

        # Store recent prices
        self.prices = []

    def decide(self, market_data):
        price = market_data.get("price")

        if price is None:
            self.logger.info("No price available. Skipping strategy decision.")
            return None

        self.prices.append(price)

        # Maintain window size
        if len(self.prices) > self.window:
            self.prices.pop(0)

        # Not enough data yet
        if len(self.prices) < self.window:
            return None

        avg_price = mean(self.prices)

        self.logger.info(f"SMA: {avg_price}, Current Price: {price}")

        # Basic trading logic
        if price > avg_price:
            return {"action": "buy", "amount": 1, "price": price}

        if price < avg_price:
            return {"action": "sell", "amount": 1, "price": price}

        return None
