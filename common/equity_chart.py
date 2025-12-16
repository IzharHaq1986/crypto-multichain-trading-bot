# equity_chart.py
#
# Terminal-safe Equity Curve Chart using Rich.
# This renders a simple ASCII line graph of PnL over time.
#

from rich.console import Console
from rich.table import Table
from rich import box


class EquityChart:
    def __init__(self):
        # Store historical PnL values
        self.history = []
        self.console = Console()

    def add_point(self, pnl_value):
        """
        Append a new PnL value to the history.
        """
        self.history.append(round(pnl_value, 4))

        # Limit history length for readability
        if len(self.history) > 80:
            self.history.pop(0)

    def render(self):
        """
        Create a Rich Table with an ASCII-style equity curve.
        """
        table = Table(title="📈 Equity Curve", box=box.ROUNDED)

        table.add_column("PnL History", style="bold magenta")

        # Build ASCII graph row
        graph = ""

        if self.history:
            min_val = min(self.history)
            max_val = max(self.history)
            span = max_val - min_val if max_val != min_val else 1

            for value in self.history:
                normalized = int(((value - min_val) / span) * 10)
                graph += "▇" * max(1, normalized) + "\n"

        else:
            graph = "(no data yet)"

        table.add_row(graph)

        return table
