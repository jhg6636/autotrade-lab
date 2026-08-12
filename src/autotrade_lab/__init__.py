"""Multi-asset systematic-trading research toolkit."""

from .catalog import CATALOG, StrategySpec
from .engine import BacktestResult, VectorBacktester

__all__ = ["CATALOG", "BacktestResult", "StrategySpec", "VectorBacktester"]
