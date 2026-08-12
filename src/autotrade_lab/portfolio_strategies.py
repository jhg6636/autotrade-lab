from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


def _prices(prices: pd.DataFrame) -> pd.DataFrame:
    if prices.empty or not prices.index.is_monotonic_increasing:
        raise ValueError("prices must be a non-empty, chronological wide DataFrame")
    return prices.astype(float)


@dataclass(slots=True)
class CrossSectionalMomentum:
    lookback: int = 126
    fraction: float = 0.2

    def weights(self, prices: pd.DataFrame) -> pd.DataFrame:
        prices = _prices(prices)
        scores = prices.pct_change(self.lookback)
        ranks = scores.rank(axis=1, pct=True)
        long = ranks >= 1 - self.fraction
        short = ranks <= self.fraction
        long_w = long.div(long.sum(axis=1).replace(0, np.nan), axis=0)
        short_w = short.div(short.sum(axis=1).replace(0, np.nan), axis=0)
        return (long_w - short_w).fillna(0)


@dataclass(slots=True)
class DualMomentum:
    lookback: int = 126

    def weights(self, prices: pd.DataFrame) -> pd.DataFrame:
        prices = _prices(prices)
        scores = prices.pct_change(self.lookback)
        winners = scores.eq(scores.max(axis=1), axis=0) & scores.gt(0)
        return winners.div(winners.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)


@dataclass(slots=True)
class InverseVolatility:
    lookback: int = 60
    target_volatility: float | None = None
    periods_per_year: int = 252

    def weights(self, prices: pd.DataFrame) -> pd.DataFrame:
        prices = _prices(prices)
        vol = prices.pct_change().rolling(self.lookback).std(ddof=0) * np.sqrt(
            self.periods_per_year
        )
        inverse = 1 / vol.replace(0, np.nan)
        weights = inverse.div(inverse.sum(axis=1), axis=0).fillna(0)
        if self.target_volatility:
            portfolio_vol = np.sqrt(((weights * vol) ** 2).sum(axis=1)).replace(0, np.nan)
            scale = (self.target_volatility / portfolio_vol).clip(upper=1.0)
            weights = weights.mul(scale, axis=0).fillna(0)
        return weights


def funding_carry_weights(funding_rates: pd.DataFrame, threshold: float = 0.0) -> pd.DataFrame:
    """Perpetual leg only: short positive funding and long negative funding, equal gross weight.

    A production portfolio must add the offsetting spot/venue leg; this signal alone is not
    delta neutral and is deliberately named as a weight generator rather than an arbitrage.
    """
    eligible = funding_rates.where(funding_rates.abs() > threshold)
    raw = -np.sign(eligible)
    return raw.div(raw.abs().sum(axis=1).replace(0, np.nan), axis=0).fillna(0)


def pairs_zscore(left: pd.Series, right: pd.Series, lookback: int = 60) -> pd.Series:
    """Distance-pair baseline using normalized log-price spread; no fitted future values."""
    spread = np.log(left) - np.log(right)
    mean = spread.rolling(lookback).mean()
    std = spread.rolling(lookback).std(ddof=0)
    return ((spread - mean) / std.replace(0, np.nan)).fillna(0)
