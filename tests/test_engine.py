import numpy as np
import pandas as pd

from autotrade_lab.engine import VectorBacktester
from autotrade_lab.strategies import STRATEGIES, BuyAndHold, MovingAverageCross


def prices(n=240):
    close = pd.Series(np.linspace(100, 160, n), index=pd.date_range("2024-01-01", periods=n))
    return pd.DataFrame(
        {"open": close, "high": close + 1, "low": close - 1, "close": close, "volume": 1000}
    )


def test_buy_and_hold_earns_on_rising_market():
    result = VectorBacktester(fee_bps=0, slippage_bps=0).run(prices(), BuyAndHold())
    assert result.metrics["total_return"] > 0.5
    assert result.positions.iloc[0] == 0


def test_signal_is_lagged_and_costs_reduce_return():
    frame = prices()
    free = VectorBacktester(0, 0).run(frame, MovingAverageCross(5, 20))
    costly = VectorBacktester(10, 10).run(frame, MovingAverageCross(5, 20))
    assert free.positions.equals(MovingAverageCross(5, 20).target(frame).shift(1).fillna(0))
    assert costly.equity.iloc[-1] < free.equity.iloc[-1]


def test_registry_contains_representative_families():
    assert {"moving_average_cross", "rsi_mean_reversion", "volatility_breakout"} <= set(STRATEGIES)
