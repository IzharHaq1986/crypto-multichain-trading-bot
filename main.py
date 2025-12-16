# ======================================================================
# main.py
#
# Entry point for the backtesting engine.
# Orchestrates:
#   - Config loading
#   - Price data loading
#   - Strategy execution
#   - Dashboard rendering
#   - Equity / drawdown chart
#   - Performance metrics
#   - Consolidated backtest summary (CSV)
#
# Fully cleaned, readable, and production-safe.
# ======================================================================

from __future__ import annotations

# ----------------------------------------------------------------------
# Standard library imports
# ----------------------------------------------------------------------
import os
import csv
from datetime import datetime, timezone

# ----------------------------------------------------------------------
# Project imports
# ----------------------------------------------------------------------
from common.config_loader import load_config
from common.fallback_price import load_price_data
from strategies.macd_strategy import MACDStrategy
from common.dashboard import render_dashboard
from common.performance import compute_performance
from common.equity_drawdown_chart import save_equity_and_drawdown


# ----------------------------------------------------------------------
# Main engine runner
# ----------------------------------------------------------------------
def run_engine() -> None:
    """
    Runs the complete backtest pipeline:
      1. Load configuration
      2. Load historical price data
      3. Run MACD strategy
      4. Render dashboard and charts
      5. Compute and print performance metrics
      6. Append consolidated summary to CSV
    """

    # --------------------------------------------------------------
    # Load configuration
    # --------------------------------------------------------------
    config = load_config("configs/example_config.yaml")

    backtest_cfg = config["strategy"]["backtest"]
    symbol = backtest_cfg["symbol"]
    start_date = backtest_cfg["start_date"]
    end_date = backtest_cfg["end_date"]

    print(f"Loading price data for: {symbol}")

    # --------------------------------------------------------------
    # Load historical price data
    # --------------------------------------------------------------
    df = load_price_data(symbol, start_date, end_date)

    if df is None or df.empty:
        print("ERROR: No price data available. Aborting.")
        return

    print("Price data loaded successfully.")

    # --------------------------------------------------------------
    # Run strategy
    # --------------------------------------------------------------
    print("Running MACD strategy...")
    strategy = MACDStrategy(config)
    df = strategy.run(df)
    print("Strategy completed.")

    # --------------------------------------------------------------
    # Render dashboard and charts
    # --------------------------------------------------------------
    print("Rendering dashboard...")
    render_dashboard(df)
    print("Dashboard rendered.")

    save_equity_and_drawdown(df)

    # --------------------------------------------------------------
    # Compute performance metrics
    # --------------------------------------------------------------
    metrics = compute_performance(df)

    total_return_pct = float(metrics["total_return"]) * 100.0
    max_drawdown_pct = float(metrics["max_drawdown"]) * 100.0
    num_trades = int(metrics["num_trades"])
    win_rate_pct = float(metrics["win_rate"]) * 100.0
    sharpe_ratio = float(metrics["sharpe"])
    sortino_ratio = float(metrics["sortino"])

    # --------------------------------------------------------------
    # Print performance summary
    # --------------------------------------------------------------
    print("\nPerformance Summary")
    print("-------------------")
    print(f"Total Return : {total_return_pct:.2f}%")
    print(f"Max Drawdown : {max_drawdown_pct:.2f}%")
    print(f"Number Trades: {num_trades}")
    print(f"Win Rate     : {win_rate_pct:.2f}%")
    print(f"Sharpe Ratio : {sharpe_ratio:.2f}")
    print(f"Sortino Ratio: {sortino_ratio:.2f}")

    # --------------------------------------------------------------
    # Append consolidated backtest summary to CSV
    # --------------------------------------------------------------
    summary_path = "backtest_summary.csv"

    summary_row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "total_return_pct": total_return_pct,
        "max_drawdown_pct": max_drawdown_pct,
        "num_trades": num_trades,
        "win_rate_pct": win_rate_pct,
        "sharpe_ratio": sharpe_ratio,
        "sortino_ratio": sortino_ratio,
    }

    write_header = not os.path.exists(summary_path)

    with open(summary_path, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(summary_row)

    print(f"\nBacktest summary appended to {summary_path}")


# ----------------------------------------------------------------------
# Script entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    run_engine()
