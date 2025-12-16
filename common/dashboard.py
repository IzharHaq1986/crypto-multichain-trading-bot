# =======================================================================
# dashboard.py
#
# Visualization module for:
#   - Price chart with Buy/Sell markers
#   - Position size annotations
#   - MACD + Signal line
#   - Normalized MACD (-1 to +1)
#
# Fully cleaned, warning-free, and compatible with non-interactive backends.
# =======================================================================

import matplotlib
matplotlib.use("Agg")  # Enables saving charts in headless environments
import matplotlib.pyplot as plt
import pandas as pd


# -----------------------------------------------------------------------
# Render dashboard and save as PNG
# -----------------------------------------------------------------------
def render_dashboard(df: pd.DataFrame) -> None:
    """
    Renders a multi-panel dashboard:
      1. Price chart with Buy/Sell and position sizes
      2. MACD + Signal
      3. Normalized MACD
    Saves chart to dashboard_output.png for non-GUI environments.
    """

    # ---------------------------------------------------------------
    # Create layout (3 stacked subplots)
    # ---------------------------------------------------------------
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    price_ax = axes[0]
    macd_ax = axes[1]
    norm_ax = axes[2]

    # ---------------------------------------------------------------
    # PRICE CHART with BUY / SELL and POSITION SIZES
    # ---------------------------------------------------------------
    price_ax.plot(df.index, df["Close"], label="Price", linewidth=1.5, color="blue")

    buy_pts = df[df["signal_flag"] == "BUY"]
    sell_pts = df[df["signal_flag"] == "SELL"]

    # BUY markers
    price_ax.scatter(
        buy_pts.index,
        buy_pts["Close"],
        color="green",
        marker="^",
        s=70,
        label="BUY"
    )

    # SELL markers
    price_ax.scatter(
        sell_pts.index,
        sell_pts["Close"],
        color="red",
        marker="v",
        s=70,
        label="SELL"
    )

    # Annotate position sizes above BUY entries
    for idx, row in buy_pts.iterrows():
        val = row.get("position_size", 0)

        # Safe scalar extraction for pandas 2.x+
        if hasattr(val, "item"):
            size = val.item()
        elif hasattr(val, "iloc"):
            size = val.iloc[0]
        else:
            size = int(val)

        if size > 0:
            price_ax.text(
                idx,
                row["Close"] * 1.01,
                f"{int(size)}",
                fontsize=8,
                color="black"
            )

    price_ax.set_title("Price Chart with Position Sizes")
    price_ax.set_ylabel("Price")
    price_ax.legend()

    # ---------------------------------------------------------------
    # MACD Indicator
    # ---------------------------------------------------------------
    macd_ax.plot(df.index, df["macd"], label="MACD", linewidth=1.2, color="purple")
    macd_ax.plot(df.index, df["signal"], label="Signal", linewidth=1.2, color="orange")

    macd_ax.axhline(0, color="black", linewidth=1)
    macd_ax.set_title("MACD Indicator")
    macd_ax.set_ylabel("MACD Value")
    macd_ax.legend()

    # ---------------------------------------------------------------
    # NORMALIZED MACD Indicator
    # ---------------------------------------------------------------
    norm_ax.plot(
        df.index,
        df["normalized_macd"],
        label="Normalized MACD",
        linewidth=1.2,
        color="teal"
    )

    norm_ax.axhline(0, color="black", linewidth=1)
    norm_ax.set_title("Normalized MACD (-1 to +1)")
    norm_ax.set_ylabel("Normalized Value")
    norm_ax.legend()

    # ---------------------------------------------------------------
    # Final layout and save output
    # ---------------------------------------------------------------
    plt.tight_layout()
    output_path = "dashboard_output.png"
    plt.savefig(output_path, dpi=200)

    print(f"Dashboard saved as {output_path}")
