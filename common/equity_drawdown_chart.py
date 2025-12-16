import matplotlib
matplotlib.use("Agg")  # Headless-safe backend

import matplotlib.pyplot as plt
import pandas as pd


def save_equity_and_drawdown(df: pd.DataFrame, output_path: str = "equity_drawdown.png") -> None:
    """
    Saves a chart with:
      - Equity curve (top)
      - Drawdown curve (bottom)
    """

    equity = df["equity"].astype(float)

    # Compute drawdown series
    rolling_max = equity.cummax()
    drawdown = (equity - rolling_max) / rolling_max

    # Create figure
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    # Equity plot
    axes[0].plot(df.index, equity)
    axes[0].set_title("Equity Curve")
    axes[0].set_ylabel("Equity")

    # Drawdown plot
    axes[1].plot(df.index, drawdown)
    axes[1].set_title("Drawdown")
    axes[1].set_ylabel("Drawdown")
    axes[1].set_xlabel("Date")

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    print(f"Equity/Drawdown chart saved as {output_path}")
