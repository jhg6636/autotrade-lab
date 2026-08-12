import numpy as np
import pandas as pd

from autotrade_lab.portfolio_strategies import (
    CrossSectionalMomentum,
    DualMomentum,
    InverseVolatility,
    funding_carry_weights,
    pairs_zscore,
)
from autotrade_lab.validation import walk_forward_splits


def wide_prices(n=20):
    idx = pd.date_range("2025-01-01", periods=n)
    return pd.DataFrame(
        {"winner": np.arange(10, 10 + n), "flat": 10, "loser": np.arange(30, 30 - n, -1)}, index=idx
    )


def test_cross_sectional_is_market_neutral_after_warmup():
    weights = CrossSectionalMomentum(lookback=3, fraction=0.34).weights(wide_prices())
    assert abs(weights.iloc[-1].sum()) < 1e-12
    assert weights.iloc[-1].winner > 0 and weights.iloc[-1].loser < 0


def test_dual_momentum_holds_only_positive_winner():
    weights = DualMomentum(3).weights(wide_prices())
    assert weights.iloc[-1].winner == 1
    assert weights.iloc[-1].loser == 0


def test_inverse_volatility_sums_to_one():
    p = wide_prices().drop(columns="flat")
    weights = InverseVolatility(3).weights(p)
    assert np.isclose(weights.iloc[-1].sum(), 1)


def test_positive_funding_produces_short_perp_leg():
    rates = pd.DataFrame({"btc": [0.001], "eth": [-0.001]})
    weights = funding_carry_weights(rates)
    assert weights.iloc[0].btc < 0 and weights.iloc[0].eth > 0


def test_pairs_zscore_has_no_warmup_signal():
    data = wide_prices()
    z = pairs_zscore(data.winner, data.flat, 5)
    assert (z.iloc[:4] == 0).all()


def test_walk_forward_never_overlaps_train_and_test():
    data = wide_prices(30)
    folds = list(walk_forward_splits(data, 10, 5))
    assert len(folds) == 4
    assert all(fold.train.index.max() < fold.test.index.min() for fold in folds)
