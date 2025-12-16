# trade_logger.py
#
# Writes trade history to a CSV file for later analysis.
#

import csv
from pathlib import Path
from datetime import datetime


class TradeLogger:

    def __init__(self, path="logs/trades.csv"):
        self.path = Path(path)

        # Create logs directory + file header if needed
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "action", "price", "pnl", "total_pnl"])

    def write(self, action, price, pnl, total_pnl):
        """
        Append a single trade event to the CSV log.
        """
        with open(self.path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.utcnow().isoformat(),
                action,
                f"{price:.4f}",
                f"{pnl:.4f}" if pnl is not None else "",
                f"{total_pnl:.4f}"
            ])
