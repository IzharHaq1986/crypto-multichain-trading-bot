# ======================================================================
# walk_forward.py
#
# Walk-forward (rolling window) validation for the MACD strategy.
#
# This script:
#   - Splits historical data into rolling train/test windows
#   - Adds a warm-up period so indicators stabilize
#   - Forces walk-forward-safe thresholds and normalization window
#   - Runs the strategy on each test window
#   - Prints detailed diagnostics per window
#   - Aggregates results into a CSV with summary statistics
#
# Designed for clarity, correctness, and robustness analysis.
# ======================================================================

from __future__ import annotations

import os
import sys
from datetime import timedelta

import pandas as pd

# ----------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# ----------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ----------------------------------------------------------------------
# Project imports
# ----------------------------------------------------------------------
from common.config_loader import load_config
from common.fallback_price import load_price_data
from strategies.macd_strategy import MACDStrategy
from common.performance import compute_performance


def walk_forward(
    symbol: str,
    start: str,
    end: str,
    train_days: int = 365,
    test_days: int = 180,
    warmup_days: int = 120,
) -> None:
    """
    Runs walk-forward validation with rolling windows.

    Each window:
      - Uses a warm-up slice before the test window
      - Executes the strategy on the combined data
      - Evaluates performance only on the true test window
    """

    # --------------------------------------------------------------
    # Load full historical data once
    # --------------------------------------------------------------
    df_all = load_price_data(symbol, start, end)

    if df_all is None or df_all.empty:
        print("ERROR: No price data available.")
        return

    df_all = df_all.sort_index()
    dates = df_all.index

    print(f"Walk-forward on {symbol}")
    print(f"Data range: {dates[0].date()} → {dates[-1].date()}")
    print("-" * 70)

    results = []
    i = 0

    while True:
        # ----------------------------------------------------------
        # Define rolling window boundaries
        # ----------------------------------------------------------
        train_start = dates[i]
        train_end = train_start + timedelta(days=train_days)

        test_start = train_end
        test_end = test_start + timedelta(days=test_days)

        if test_end > dates[-1]:
            break

        # ----------------------------------------------------------
        # Prepare warm-up + test data
        # ----------------------------------------------------------
        warmup_start = test_start - timedelta(days=warmup_days)

        test_df = df_all.loc[
            (df_all.index >= warmup_start) &
            (df_all.index < test_end)
        ].copy()

        # ----------------------------------------------------------
        # Load config and force walk-forward-safe parameters
        # ----------------------------------------------------------
        cfg = load_config("configs/example_config.yaml")

        # Disable trade logging during sweeps
        cfg["strategy"]["log_trades"] = False

        # Reset capital per window
        cfg["strategy"]["position_sizing"]["account_balance"] = (
            cfg["strategy"]["backtest"]["initial_capital"]
        )

        # Looser thresholds for short windows
        cfg["strategy"]["thresholds"]["normalized_buy"] = -0.50
        cfg["strategy"]["thresholds"]["normalized_sell"] = 0.50

        # Shorter normalization window for stability
        cfg["strategy"]["normalization"]["window"] = 60

        print(f"Window {test_start.date()} → {test_end.date()}")
        print(
            f"  Thresholds: BUY={cfg['strategy']['thresholds']['normalized_buy']}, "
            f"SELL={cfg['strategy']['thresholds']['normalized_sell']}"
        )
        print(
            f"  Normalization window: {cfg['strategy']['normalization']['window']}"
        )

        # ----------------------------------------------------------
        # Run strategy
        # ----------------------------------------------------------
        strategy = MACDStrategy(cfg)
        out = strategy.run(test_df)

        # Keep only the real test window (exclude warm-up)
        out = out.loc[
            (out.index >= test_start) &
            (out.index < test_end)
        ]

        # ----------------------------------------------------------
        # Diagnostics
        # ----------------------------------------------------------
        equity_start = float(out["equity"].iloc[0])
        equity_end = float(out["equity"].iloc[-1])

        signal_counts = out["signal_flag"].value_counts(
            dropna=False
        ).to_dict()

        position_changes = int(
            out["position_size"]
            .diff()
            .fillna(0)
            .abs()
            .sum()
        )

        print(f"  Equity: {equity_start:.2f} → {equity_end:.2f}")
        print(f"  Signals: {signal_counts}")
        print(f"  Position changes: {position_changes}")

        # ----------------------------------------------------------
        # Performance metrics
        # ----------------------------------------------------------
        metrics = compute_performance(out)

        window_result = {
            "train_start": train_start.date().isoformat(),
            "train_end": train_end.date().isoformat(),
            "test_start": test_start.date().isoformat(),
            "test_end": test_end.date().isoformat(),
            "return_pct": float(metrics["total_return"]) * 100.0,
            "max_dd_pct": float(metrics["max_drawdown"]) * 100.0,
            "trades": int(metrics["num_trades"]),
            "win_rate_pct": float(metrics["win_rate"]) * 100.0,
            "sharpe": float(metrics["sharpe"]),
            "sortino": float(metrics["sortino"]),
        }

        print("  Performance:", window_result)
        print("-" * 70)

        results.append(window_result)

        # Advance by test window length
        i += test_days

    # --------------------------------------------------------------
    # Aggregate and save walk-forward results
    # --------------------------------------------------------------
    if not results:
        print("No walk-forward windows were evaluated.")
        return

    wf_df = pd.DataFrame(results)
    wf_df.to_csv("walk_forward_results.csv", index=False)

    print("\nWalk-Forward Summary")
    print("--------------------")
    print(f"Windows tested : {len(wf_df)}")
    print(f"Avg Return     : {wf_df['return_pct'].mean():.2f}%")
    print(f"Worst Return   : {wf_df['return_pct'].min():.2f}%")
    print(f"Avg Max DD     : {wf_df['max_dd_pct'].mean():.2f}%")
    print(f"Avg Sharpe     : {wf_df['sharpe'].mean():.2f}")
    print(f"Avg Sortino    : {wf_df['sortino'].mean():.2f}")
    print("\nSaved walk_forward_results.csv")


# ----------------------------------------------------------------------
# Script entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    cfg = load_config("configs/example_config.yaml")
    bt = cfg["strategy"]["backtest"]

    walk_forward(
        symbol=bt["symbol"],
        start=bt["start_date"],
        end=bt["end_date"],
        train_days=365,
        test_days=180,
        warmup_days=120,
    )
