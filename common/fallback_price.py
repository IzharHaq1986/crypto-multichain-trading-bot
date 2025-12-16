# =======================================================================
# fallback_price.py
#
# Loads historical price data:
#   1. Tries yfinance
#   2. Falls back to CSV if yfinance fails
#
# Guarantees:
#   - DataFrame has a 'Close' column for strategies to use
#   - Index is sorted
#   - MultiIndex columns from yfinance are flattened safely
# =======================================================================

import os
import pandas as pd

try:
    import yfinance as yf
except ImportError:
    yf = None


# -----------------------------------------------------------------------
# Internal helper: ensure there is a 'Close' column
# -----------------------------------------------------------------------
def _ensure_close_column(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """
    Normalizes yfinance output so that the returned DataFrame always
    has a 'Close' column.

    Handles:
      - MultiIndex columns
      - Single-column series
      - Ticker-prefixed columns
      - Strange layouts where all columns are the ticker symbol
    """

    # Already good
    if "Close" in df.columns:
        return df

    # If MultiIndex, try to extract standard OHLC names
    if isinstance(df.columns, pd.MultiIndex):
        possible_fields = ["Open", "High", "Low", "Close", "Adj Close", "AdjClose", "Volume"]
        new_cols = []

        for col in df.columns:
            # col is a tuple representing levels
            name = None
            for part in col:
                if part in possible_fields:
                    name = part
                    break
            if name is None:
                # Fallback: join parts
                name = "_".join(str(p) for p in col if p is not None)
            new_cols.append(name)

        df = df.copy()
        df.columns = new_cols

        # After flattening, we might now have 'Close'
        if "Close" in df.columns:
            return df

    # If we still do not have 'Close', try some common patterns
    # e.g. ['AAPL_Close', ...] or lowercase names.
    lower_map = {c.lower(): c for c in df.columns}
    if "close" in lower_map:
        real_name = lower_map["close"]
        df = df.copy()
        df.rename(columns={real_name: "Close"}, inplace=True)
        return df

    # If one of the columns is exactly the symbol, treat that as Close
    if symbol in df.columns:
        df = df[[symbol]].copy()
        df.columns = ["Close"]
        return df

    # As a last resort: take the first column and call it Close
    first_col = df.columns[0]
    df = df[[first_col]].copy()
    df.columns = ["Close"]
    return df


# -----------------------------------------------------------------------
# Public API: load_price_data
# -----------------------------------------------------------------------
def load_price_data(symbol: str, start: str, end: str) -> pd.DataFrame:
    """
    Loads price data for the given symbol between start and end dates.

    Order of attempts:
      1. yfinance
      2. local CSV (data/<symbol>.csv)

    Always returns a DataFrame with:
      - Datetime index
      - At least one column named 'Close'
    """

    # ---------------------------------------------------------------
    # Try yfinance first
    # ---------------------------------------------------------------
    if yf is not None:
        try:
            # Explicitly set auto_adjust to avoid yfinance default-change warnings
            df = yf.download(symbol, start=start, end=end, auto_adjust=False)

            if df is not None and not df.empty:
                # If columns are MultiIndex like ('Close', 'AAPL'),
                # flatten them to simple names: 'Close', 'High', etc.
                if isinstance(df.columns, pd.MultiIndex):
                    df = df.copy()
                    df.columns = [col[0] for col in df.columns]

                # Ensure datetime index and sorted order
                if not isinstance(df.index, pd.DatetimeIndex):
                    df.index = pd.to_datetime(df.index)

                df = df.sort_index()

                # At this point we should have a 'Close' column
                if "Close" not in df.columns:
                    print("[WARN] 'Close' column missing after flatten, columns:", df.columns.tolist())

                return df

            print("[WARN] yfinance returned no data.")

        except Exception as e:
            print(f"[WARN] yfinance exception: {e}")

    # ---------------------------------------------------------------
    # CSV fallback
    # ---------------------------------------------------------------
    csv_path = f"data/{symbol}.csv"

    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)

            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
                df = df.set_index("Date")

            df = df.sort_index()
            df = _ensure_close_column(df, symbol)
            return df

        except Exception as e:
            print(f"[ERROR] CSV load failed: {e}")

    # ---------------------------------------------------------------
    # No data source worked
    # ---------------------------------------------------------------
    print("[ERROR] No price data could be loaded.")
    return pd.DataFrame()
