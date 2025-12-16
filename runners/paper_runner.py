from __future__ import annotations

from brokers.paper import PaperBroker
from brokers.base import OrderRequest
from strategies.macd_strategy import MACDStrategy


def run_paper(symbol: str, df, config):
    """
    Runs the MACD strategy using the PaperBroker.
    Executes orders via the broker instead of direct balance math.
    """

    broker = PaperBroker(
        starting_balance=config["strategy"]["backtest"]["initial_capital"]
    )

    strategy = MACDStrategy(config)

    position = 0.0

    for index, row in df.iterrows():
        price = float(row["Close"])
        broker.set_last_price(symbol, price)

        signal = row.get("signal_flag", "HOLD")

        if signal == "BUY" and position == 0:
            qty = strategy.calculate_position_size(price)
            result = broker.place_order(
                OrderRequest(
                    symbol=symbol,
                    side="BUY",
                    quantity=qty,
                )
            )
            if result.status == "FILLED":
                position = qty

        elif signal == "SELL" and position > 0:
            result = broker.place_order(
                OrderRequest(
                    symbol=symbol,
                    side="SELL",
                    quantity=position,
                )
            )
            if result.status == "FILLED":
                position = 0.0

    return broker.get_balance()
