# strategies/rsi_strategy.py

from strategies.base_strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.window = config.get("strategy", {}).get("rsi_window", 14)
        self.prices = []

    def _calculate_rsi(self, prices):
        if len(prices) < self.window:
            return None

        gains = []
        losses = []

        for i in range(1, len(prices)):
            delta = prices[i] - prices[i-1]
            if delta > 0:
                gains.append(delta)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(delta))

        avg_gain = sum(gains[-self.window:]) / self.window
        avg_loss = sum(losses[-self.window:]) / self.window if sum(losses[-self.window:]) != 0 else 1e-6

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def decide(self, market_data):
        price = market_data.get("price")
        if price is None:
            return None

        self.prices.append(price)

        rsi = self._calculate_rsi(self.prices)

        if rsi is None:
            return None

        self.logger.info(f"RSI: {round(rsi, 2)}, Price: {price}")

        # Basic RSI rules
        if rsi < 30:
            return {"action": "buy", "amount": 1, "price": price}

        if rsi > 70:
            return {"action": "sell", "amount": 1, "price": price}

        return None
