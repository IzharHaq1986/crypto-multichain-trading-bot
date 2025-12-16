# ======================================================================
# parameter_sweep.py
#
# Runs a simple grid search over normalized MACD thresholds
# to compare strategy performance across multiple configurations.
#
# This script:
#   - Safely fixes PYTHONPATH so project imports work
#   - Loads price data once
#   - Runs the MACD strategy for each parameter pair
#   - Prints results sorted by total return
#
# Designed for clarity and easy modification.
# ======================================================================

import sys
import os
import copy

# ----------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# This allows imports like `common.*` and `strategies.*`
# ----------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ----------------------------------------------------------------------
# Project imports (safe after PYTHONPATH fix)
# ----------------------------------------------------------------------
from common.config_loader import load_config
from common.fallback_price import load_price_data
from strategies.macd_strategy import MACDStrategy
from common.performance import compute_performance


def main():
    """
    Entry point for parameter sweep.
    """

    # --------------------------------------------------------------
    # Load base configuration
    # --------------------------------------------------------------
    base_config = load_config("configs/example_config.yaml")

    symbol = base_config["strategy"]["backtest"]["symbol"]
    start = base_config["strategy"]["backtest"]["start_date"]
    end = base_config["strategy"]["backtest"]["end_date"]

    # --------------------------------------------------------------
    # Load price data once (important for fair comparison)
    # --------------------------------------------------------------
    print(f"Loading price data for sweep: {symbol}")
    df_price = load_price_data(symbol, start, end)

    if df_price is None or df_price.empty:
        print("ERROR: No price data available. Aborting sweep.")
        return

    # --------------------------------------------------------------
    # Parameter ranges to test
    # Adjust these values to widen or narrow the search
    # --------------------------------------------------------------
    buy_levels = [-0.80, -0.70, -0.60]
    sell_levels = [0.60, 0.70, 0.80]

    results = []

    # --------------------------------------------------------------
    # Grid search loop
    # --------------------------------------------------------------
    for buy in buy_levels:
        for sell in sell_levels:

            # Sanity check: BUY threshold must be below SELL threshold
            if buy >= sell:
                continue

            # Deep copy config so each run is isolated
            cfg = copy.deepcopy(base_config)
            cfg["strategy"]["thresholds"]["normalized_buy"] = buy
            cfg["strategy"]["thresholds"]["normalized_sell"] = sell
            cfg["strategy"]["log_trades"] = False


            # Run strategy
            strategy = MACDStrategy(cfg)
            df_result = strategy.run(df_price.copy())

            # Compute performance metrics
            metrics = compute_performance(df_result)

            results.append({
                "buy_threshold": buy,
                "sell_threshold": sell,
                "total_return": float(metrics["total_return"]),
                "max_drawdown": float(metrics["max_drawdown"]),
                "num_trades": int(metrics["num_trades"]),
                "win_rate": float(metrics["win_rate"]),
            })

    # --------------------------------------------------------------
    # Sort results by total return (descending)
    # --------------------------------------------------------------
    results = sorted(
        results,
        key=lambda x: x["total_return"],
        reverse=True
    )

    # --------------------------------------------------------------
    # Display results
    # --------------------------------------------------------------
    print("\nParameter Sweep Results")
    print("-----------------------")

    for r in results:
        print(
            f"BUY={r['buy_threshold']:.2f}, "
            f"SELL={r['sell_threshold']:.2f} | "
            f"Return={r['total_return'] * 100:.2f}%, "
            f"DD={r['max_drawdown'] * 100:.2f}%, "
            f"Trades={r['num_trades']}, "
            f"WinRate={r['win_rate'] * 100:.2f}%"
        )


# ----------------------------------------------------------------------
# Script entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
