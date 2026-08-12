from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .strategies import Strategy


@dataclass(frozen=True, slots=True)
class BacktestResult:
    equity: pd.Series
    returns: pd.Series
    positions: pd.Series
    turnover: pd.Series
    metrics: dict[str, float]


class VectorBacktester:
    """A deliberately small close-to-close engine with lagged signals and explicit costs."""

    def __init__(self, fee_bps: float = 5, slippage_bps: float = 5, periods_per_year: int = 252):
        self.cost_rate = (fee_bps + slippage_bps) / 10_000
        self.periods_per_year = periods_per_year

    def run(
        self, frame: pd.DataFrame, strategy: Strategy, initial_cash: float = 1_000_000
    ) -> BacktestResult:
        target = strategy.target(frame).clip(-1, 1).fillna(0)
        position = target.shift(1).fillna(0)  # signals formed at t execute for return t+1
        asset_return = frame.close.pct_change().fillna(0)
        turnover = position.diff().abs().fillna(position.abs())
        net = position * asset_return - turnover * self.cost_rate
        equity = initial_cash * (1 + net).cumprod()
        peak = equity.cummax()
        drawdown = equity / peak - 1
        volatility = net.std(ddof=0) * np.sqrt(self.periods_per_year)
        sharpe = net.mean() * self.periods_per_year / volatility if volatility else 0.0
        years = max(len(net) / self.periods_per_year, 1 / self.periods_per_year)
        cagr = (equity.iloc[-1] / initial_cash) ** (1 / years) - 1
        metrics = {
            "total_return": float(equity.iloc[-1] / initial_cash - 1),
            "cagr": float(cagr),
            "annual_volatility": float(volatility),
            "sharpe_zero_rf": float(sharpe),
            "max_drawdown": float(drawdown.min()),
            "turnover": float(turnover.sum()),
        }
        return BacktestResult(equity, net, position, turnover, metrics)
