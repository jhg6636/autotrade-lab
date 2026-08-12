from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True, slots=True)
class WalkForwardFold:
    train: pd.DataFrame
    test: pd.DataFrame


def walk_forward_splits(
    frame: pd.DataFrame, train_size: int, test_size: int
) -> Iterator[WalkForwardFold]:
    if train_size <= 0 or test_size <= 0:
        raise ValueError("train_size and test_size must be positive")
    start = 0
    while start + train_size + test_size <= len(frame):
        boundary = start + train_size
        yield WalkForwardFold(
            frame.iloc[start:boundary], frame.iloc[boundary : boundary + test_size]
        )
        start += test_size


def parameter_stability(
    frame: pd.DataFrame,
    parameter_values: list[object],
    evaluate: Callable[[pd.DataFrame, object], float],
) -> pd.Series:
    """Return every tested result so callers cannot silently retain only the best trial."""
    return pd.Series(
        {str(value): evaluate(frame, value) for value in parameter_values}, name="score"
    )
