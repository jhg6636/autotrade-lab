from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
import pandas as pd


def _validate(frame: pd.DataFrame) -> None:
    required = {"open", "high", "low", "close", "volume"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing OHLCV columns: {sorted(missing)}")
    if not frame.index.is_monotonic_increasing:
        raise ValueError("Input must be sorted oldest to newest")


class Strategy(ABC):
    name: str

    @abstractmethod
    def target(self, frame: pd.DataFrame) -> pd.Series:
        """Return desired exposure in [-1, 1], calculated without future information."""


@dataclass(slots=True)
class MovingAverageCross(Strategy):
    fast: int = 20
    slow: int = 100
    name: str = "moving_average_cross"

    def target(self, frame: pd.DataFrame) -> pd.Series:
        _validate(frame)
        fast = frame.close.rolling(self.fast).mean()
        slow = frame.close.rolling(self.slow).mean()
        return pd.Series(np.where(fast > slow, 1.0, -1.0), index=frame.index).where(slow.notna(), 0)


@dataclass(slots=True)
class DonchianBreakout(Strategy):
    lookback: int = 55
    exit_lookback: int = 20
    name: str = "donchian_breakout"

    def target(self, frame: pd.DataFrame) -> pd.Series:
        _validate(frame)
        upper = frame.high.shift(1).rolling(self.lookback).max()
        lower = frame.low.shift(1).rolling(self.lookback).min()
        exit_high = frame.high.shift(1).rolling(self.exit_lookback).max()
        exit_low = frame.low.shift(1).rolling(self.exit_lookback).min()
        out = pd.Series(0.0, index=frame.index)
        state = 0.0
        for i in range(len(frame)):
            price = frame.close.iloc[i]
            if pd.notna(upper.iloc[i]) and price > upper.iloc[i]:
                state = 1.0
            elif pd.notna(lower.iloc[i]) and price < lower.iloc[i]:
                state = -1.0
            elif (
                state > 0
                and pd.notna(exit_low.iloc[i])
                and price < exit_low.iloc[i]
                or state < 0
                and pd.notna(exit_high.iloc[i])
                and price > exit_high.iloc[i]
            ):
                state = 0.0
            out.iloc[i] = state
        return out


@dataclass(slots=True)
class TimeSeriesMomentum(Strategy):
    lookback: int = 126
    deadband: float = 0.0
    name: str = "time_series_momentum"

    def target(self, frame: pd.DataFrame) -> pd.Series:
        _validate(frame)
        momentum = frame.close.pct_change(self.lookback)
        raw = np.where(
            momentum > self.deadband, 1.0, np.where(momentum < -self.deadband, -1.0, 0.0)
        )
        return pd.Series(raw, index=frame.index).where(momentum.notna(), 0.0)


@dataclass(slots=True)
class RsiMeanReversion(Strategy):
    period: int = 14
    low: float = 30
    high: float = 70
    name: str = "rsi_mean_reversion"

    def target(self, frame: pd.DataFrame) -> pd.Series:
        _validate(frame)
        delta = frame.close.diff()
        gain = delta.clip(lower=0).ewm(alpha=1 / self.period, adjust=False).mean()
        loss = -delta.clip(upper=0).ewm(alpha=1 / self.period, adjust=False).mean()
        rsi = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
        out = pd.Series(0.0, index=frame.index)
        state = 0.0
        for i, value in enumerate(rsi):
            if pd.isna(value):
                continue
            if value < self.low:
                state = 1.0
            elif value > self.high:
                state = -1.0
            elif state > 0 and value >= 50 or state < 0 and value <= 50:
                state = 0.0
            out.iloc[i] = state
        return out


@dataclass(slots=True)
class BollingerMeanReversion(Strategy):
    lookback: int = 20
    width: float = 2.0
    name: str = "bollinger_mean_reversion"

    def target(self, frame: pd.DataFrame) -> pd.Series:
        _validate(frame)
        mean = frame.close.rolling(self.lookback).mean()
        std = frame.close.rolling(self.lookback).std(ddof=0)
        z = (frame.close - mean) / std.replace(0, np.nan)
        return (-z / self.width).clip(-1, 1).fillna(0)


@dataclass(slots=True)
class VolatilityBreakout(Strategy):
    k: float = 0.5
    name: str = "volatility_breakout"

    def target(self, frame: pd.DataFrame) -> pd.Series:
        _validate(frame)
        previous_range = (frame.high - frame.low).shift(1)
        trigger = frame.open + self.k * previous_range
        return (frame.close > trigger).astype(float).where(trigger.notna(), 0.0)


@dataclass(slots=True)
class GapFade(Strategy):
    threshold: float = 0.02
    name: str = "gap_fade"

    def target(self, frame: pd.DataFrame) -> pd.Series:
        _validate(frame)
        gap = frame.open / frame.close.shift(1) - 1
        return pd.Series(
            np.where(gap > self.threshold, -1.0, np.where(gap < -self.threshold, 1.0, 0.0)),
            index=frame.index,
        )


@dataclass(slots=True)
class VolumeMomentum(Strategy):
    return_lookback: int = 20
    volume_lookback: int = 20
    multiplier: float = 1.5
    name: str = "volume_momentum"

    def target(self, frame: pd.DataFrame) -> pd.Series:
        _validate(frame)
        momentum = frame.close.pct_change(self.return_lookback)
        active = (
            frame.volume
            > frame.volume.shift(1).rolling(self.volume_lookback).mean() * self.multiplier
        )
        return pd.Series(np.sign(momentum), index=frame.index).where(active & momentum.notna(), 0.0)


@dataclass(slots=True)
class BuyAndHold(Strategy):
    name: str = "buy_and_hold"

    def target(self, frame: pd.DataFrame) -> pd.Series:
        _validate(frame)
        return pd.Series(1.0, index=frame.index)


STRATEGIES = {
    cls().name: cls
    for cls in [
        MovingAverageCross,
        DonchianBreakout,
        TimeSeriesMomentum,
        RsiMeanReversion,
        BollingerMeanReversion,
        VolatilityBreakout,
        GapFade,
        VolumeMomentum,
        BuyAndHold,
    ]
}
