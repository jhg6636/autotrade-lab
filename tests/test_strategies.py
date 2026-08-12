import numpy as np
import pandas as pd
import pytest

from autotrade_lab.strategies import BollingerMeanReversion, TimeSeriesMomentum


def frame(close):
    close = pd.Series(close, index=pd.date_range("2025-01-01", periods=len(close)))
    return pd.DataFrame(
        {"open": close, "high": close + 1, "low": close - 1, "close": close, "volume": 100}
    )


def test_momentum_turns_long_after_positive_history():
    signal = TimeSeriesMomentum(lookback=3).target(frame(np.arange(1, 10)))
    assert signal.iloc[-1] == 1


def test_mean_reversion_is_bounded():
    signal = BollingerMeanReversion(5).target(frame([10, 10, 10, 10, 10, 20, 5]))
    assert signal.abs().max() <= 1


def test_unsorted_input_is_rejected():
    data = frame([1, 2, 3]).sort_index(ascending=False)
    with pytest.raises(ValueError):
        TimeSeriesMomentum(2).target(data)
