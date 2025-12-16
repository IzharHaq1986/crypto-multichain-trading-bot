# atr_filter.py
#
# Simple ATR-based volatility filter.
# We approximate True Range from price changes:
#   TR_t = |price_t - price_{t-1}|
# ATR is an EMA over TR.
# We then compare ATR relative to price:
#   atr_pct = ATR / price
# If atr_pct >= min_atr_pct  → volatility is "high enough" to trade.
#

class ATRFilter:

    def __init__(self, period=14, min_atr_pct=0.005):
        """
        period       : number of periods for ATR EMA
        min_atr_pct  : minimum ATR as fraction of price (e.g. 0.005 = 0.5%)
        """

        self.period = period
        self.min_atr_pct = min_atr_pct

        self.prev_price = None
        self.atr = None
        self.ready = False

    def update(self, price):
        """
        Update ATR with a new price.
        Returns current ATR value (may be None at start).
        """

        if self.prev_price is None:
            # First sample, cannot compute TR yet
            self.prev_price = price
            return self.atr

        true_range = abs(price - self.prev_price)
        self.prev_price = price

        alpha = 2 / (self.period + 1)

        if self.atr is None:
            # Initialize ATR with first TR
            self.atr = true_range
        else:
            # EMA smoothing
            self.atr = (alpha * true_range) + ((1 - alpha) * self.atr)

        # Consider ATR "ready" after at least 'period' updates
        if not self.ready and self.atr is not None:
            self.ready = True

        return self.atr

    def is_tradable(self, price):
        """
        Returns True if volatility is sufficient to allow trading.
        """

        if not self.ready or self.atr is None or price == 0:
            return False

        atr_pct = self.atr / price

        return atr_pct >= self.min_atr_pct

    def debug_info(self, price):
        """
        Returns a small dict useful for logging/debugging.
        """

        if self.atr is None or price == 0:
            return {
                "atr": None,
                "atr_pct": None
            }

        return {
            "atr": round(self.atr, 6),
            "atr_pct": round(self.atr / price, 6)
        }
