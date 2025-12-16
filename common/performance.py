# ======================================================================
# performance.py
#
# Computes performance metrics for backtest results.
# Metrics included:
#   - Total Return
#   - Max Drawdown
#   - Number of Trades
#   - Win Rate
#   - Sharpe Ratio
#   - Sortino Ratio
#
# All functions are indentation-safe and human-readable.
# ======================================================================

from __future__ import annotations

import numpy as np
import pandas as pd


# ----------------------------------------------------------------------
# Sharpe Ratio
# ----------------------------------------------------------------------
def compute_sharpe_ratio(
    equity: pd.Series,
    risk_free_rate: float = 0.0
) -> float:
    """
    Computes the annualized Sharpe ratio using daily returns.
    """

    returns = equity.pct_change().dropna()

    if returns.empty or returns.std() == 0:
        return 0.0

    daily_rf = risk_free_rate / 252.0
    sharpe = (returns.mean() - daily_rf) / returns.std()

    return float(np.sqrt(252) * sharpe)


# ----------------------------------------------------------------------
# Sortino Ratio
# ----------------------------------------------------------------------
def compute_sortino_ratio(
    equity: pd.Series,
    risk_free_rate: float = 0.0
) -> float:
    """
    Computes the annualized Sortino ratio using downside deviation.
    """

    returns = equity.pct_change().dropna()
    downside = returns[returns < 0]

    if downside.empty or downside.std() == 0:
        return 0.0

    daily_rf = risk_free_rate / 252.0
    sortino = (returns.mean() - daily_rf) / downside.std()

    return float(np.sqrt(252) * sortino)


# ----------------------------------------------------------------------
# Main Performance Aggregator
# ----------------------------------------------------------------------
def compute_performance(df: pd.DataFrame) -> dict:
    """
    Computes all performance metrics from a backtest DataFrame.
    Expects 'equity' and 'position_size' columns to exist.
    """

    equity = df["equity"]

    # --------------------------------------------------------------
    # Total Return
    # --------------------------------------------------------------
    total_return = (equity.iloc[-1] / equity.iloc[0]) - 1.0

    # --------------------------------------------------------------
    # Max Drawdown
    # --------------------------------------------------------------
    rolling_max = equity.cummax()
    drawdown = (equity - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    # --------------------------------------------------------------
    # Number of Trades
    # --------------------------------------------------------------
    position_changes = df["position_size"].diff().fillna(0)
    trade_entries = (position_changes > 0).sum()
    trade_exits = (position_changes < 0).sum()
    num_trades = int(min(trade_entries, trade_exits))

    # --------------------------------------------------------------
    # Win Rate (based on equity increases)
    # --------------------------------------------------------------
    wins = 0
    losses = 0
    prev_equity = equity.iloc[0]

    for val in equity:
        if val > prev_equity:
            wins += 1
        elif val < prev_equity:
            losses += 1
        prev_equity = val

    win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0.0

    # --------------------------------------------------------------
    # Risk-Adjusted Metrics
    # --------------------------------------------------------------
    sharpe = compute_sharpe_ratio(equity)
    sortino = compute_sortino_ratio(equity)

    # --------------------------------------------------------------
    # Return all metrics
    # --------------------------------------------------------------
    return {
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "num_trades": num_trades,
        "win_rate": win_rate,
        "sharpe": sharpe,
        "sortino": sortino,
    }
