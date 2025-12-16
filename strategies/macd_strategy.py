# ======================================================================
# macd_strategy.py
#
# MACD-based trading strategy with:
#   - Standard MACD
#   - Normalized MACD (-1 to +1)
#   - Buy / Sell / Hold signal generation
#   - Risk-based position sizing
#   - Backtest execution
#   - Transaction costs (commission + slippage)
#   - Optional trade logging to CSV
#
# IMPORTANT:
# This version reads the normalization window from config.
# This is REQUIRED for walk-forward validation to work correctly.
# ======================================================================

from __future__ import annotations

import pandas as pd


class MACDStrategy:
    """
    MACD trading strategy.

    Full pipeline:
      1. Compute MACD
      2. Normalize MACD
      3. Generate signals
      4. Execute backtest
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(self, config: dict) -> None:
        self.config = config

    # ------------------------------------------------------------------
    # Compute MACD and signal line
    # ------------------------------------------------------------------
    def compute_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        macd_cfg = self.config["strategy"]["macd"]

        fast = macd_cfg["fast_period"]
        slow = macd_cfg["slow_period"]
        signal_period = macd_cfg["signal_period"]

        # Exponential moving averages
        df.loc[:, "ema_fast"] = df["Close"].ewm(
            span=fast,
            adjust=False
        ).mean()

        df.loc[:, "ema_slow"] = df["Close"].ewm(
            span=slow,
            adjust=False
        ).mean()

        # MACD and signal line
        df.loc[:, "macd"] = df["ema_fast"] - df["ema_slow"]
        df.loc[:, "signal"] = df["macd"].ewm(
            span=signal_period,
            adjust=False
        ).mean()

        return df

    # ------------------------------------------------------------------
    # Normalize MACD into range [-1, +1]
    # ------------------------------------------------------------------
    def compute_normalized_macd(
        self,
        df: pd.DataFrame,
        window: int = 200,
    ) -> pd.DataFrame:
        """
        Normalizes MACD using rolling min/max.

        NOTE:
        The normalization window is pulled from config if present.
        This is critical for walk-forward validation.
        """

        # --------------------------------------------------------------
        # Use config-driven normalization window when available
        # --------------------------------------------------------------
        window = int(
            self.config["strategy"]["normalization"].get("window", window)
        )

        macd_min = df["macd"].rolling(window).min()
        macd_max = df["macd"].rolling(window).max()

        denom = (macd_max - macd_min).replace(0, pd.NA)
        normalized = 2 * ((df["macd"] - macd_min) / denom) - 1

        df.loc[:, "normalized_macd"] = normalized.fillna(0.0)

        return df

    # ------------------------------------------------------------------
    # Risk-based position sizing
    # ------------------------------------------------------------------
    def calculate_position_size(self, price: float) -> int:
        """
        Calculates position size using risk-based sizing.
        """

        ps = self.config["strategy"]["position_sizing"]

        if not ps["enabled"]:
            return 1

        balance = ps["account_balance"]
        risk_fraction = ps["risk_per_trade"]
        stop_loss_pct = ps["stop_loss_pct"]

        risk_amount = balance * risk_fraction
        stop_loss_distance = price * stop_loss_pct

        if stop_loss_distance <= 0:
            return 1

        size = int(risk_amount / stop_loss_distance)

        return max(size, 1)

    # ------------------------------------------------------------------
    # Generate BUY / SELL / HOLD signals
    # ------------------------------------------------------------------
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        thresholds = self.config["strategy"]["thresholds"]

        buy_thr = thresholds["normalized_buy"]
        sell_thr = thresholds["normalized_sell"]

        df.loc[:, "signal_flag"] = "HOLD"

        df.loc[
            df["normalized_macd"] <= buy_thr,
            "signal_flag"
        ] = "BUY"

        df.loc[
            df["normalized_macd"] >= sell_thr,
            "signal_flag"
        ] = "SELL"

        return df

    # ------------------------------------------------------------------
    # Backtest execution with transaction costs
    # ------------------------------------------------------------------
    def run_backtest(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes a long-only backtest with:
          - Commission per trade
          - Percentage slippage
        """

        initial_capital = self.config["strategy"]["backtest"]["initial_capital"]
        capital = float(initial_capital)
        position = 0

        commission = self.config["strategy"].get("commission_per_trade", 0.0)
        slippage = self.config["strategy"].get("slippage_pct", 0.0)

        # Initialize tracking columns
        df.loc[:, "position_size"] = 0
        df.loc[:, "equity"] = float(capital)

        trades = []
        entry_price_eff = None
        entry_index = None

        for index, row in df.iterrows():

            # Safe scalar extraction
            close_val = row["Close"]
            price = close_val.item() if hasattr(close_val, "item") else float(close_val)

            signal = str(row.get("signal_flag", "HOLD")).strip()

            # ----------------------------------------------------------
            # BUY
            # ----------------------------------------------------------
            if signal == "BUY" and position == 0:
                size = self.calculate_position_size(price)

                if size > 0:
                    entry_price_eff = price * (1.0 + slippage)
                    cost = (size * entry_price_eff) + commission

                    if cost <= capital:
                        capital -= cost
                        position = size
                        entry_index = index
                        df.loc[index, "position_size"] = size

            # ----------------------------------------------------------
            # SELL
            # ----------------------------------------------------------
            elif signal == "SELL" and position > 0:
                exit_price_eff = price * (1.0 - slippage)

                capital += (position * exit_price_eff) - commission

                pnl = (
                    (exit_price_eff - entry_price_eff) * position
                    - (2 * commission)
                )

                trades.append({
                    "entry_date": entry_index,
                    "entry_price": entry_price_eff,
                    "exit_date": index,
                    "exit_price": exit_price_eff,
                    "position_size": position,
                    "pnl": pnl,
                })

                position = 0
                df.loc[index, "position_size"] = 0

            # ----------------------------------------------------------
            # Equity update (mark-to-market)
            # ----------------------------------------------------------
            df.loc[index, "equity"] = float(
                capital + (position * price)
            )

        # --------------------------------------------------------------
        # Save trade log only if enabled
        # --------------------------------------------------------------
        if self.config["strategy"].get("log_trades", True):
            pd.DataFrame(trades).to_csv("trade_log.csv", index=False)
            print("Trade log saved as trade_log.csv")

        return df

    # ------------------------------------------------------------------
    # FULL STRATEGY PIPELINE (entry point)
    # ------------------------------------------------------------------
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Full execution pipeline.
        """

        df = self.compute_macd(df)
        df = self.compute_normalized_macd(df)
        df = self.generate_signals(df)
        df = self.run_backtest(df)

        return df
