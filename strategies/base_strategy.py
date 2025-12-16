# strategies/base_strategy.py

class BaseStrategy:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def decide(self, market_data):
        """
        Implement strategy logic.
        Must return either:
        - None (no trade)
        - dict(action="buy"/"sell", amount=..., price=...)
        """
        raise NotImplementedError("decide() must be implemented by strategy subclasses")
