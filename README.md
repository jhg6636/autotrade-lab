# autotrade-lab

A multi-asset laboratory for researching systematic strategies across Korean-listed stocks,
ETFs, and crypto markets. The project separates research, simulation, paper trading, risk,
and live execution so a promising backtest cannot accidentally become a real order.

> This is research software, not investment advice. No strategy is assumed profitable.
> Live trading is disabled by default.

## Current scope

- 35 strategy hypotheses catalogued across 13 families
- 9 executable single-instrument and 5 portfolio/pairs/carry baseline strategies
- A look-ahead-safe vector backtester with fees, slippage, turnover, drawdown, and Sharpe
- Common broker boundary for Toss Securities and Binance/Upbit-compatible transports
- Fail-closed live-trading guard and portfolio-level risk checks
- KRX equities/ETFs through Toss Securities and crypto spot/perpetual instrument models

Before historical data is collected, every idea is treated as an equal `hypothesis` regardless
of whether it came from a journal, a trader, a community post, source code, or a video. Source
type is provenance metadata, not a quality score. Catalog status describes implementation
progress only; promotion happens later through the same data and execution-aware tests.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

```python
import pandas as pd
from autotrade_lab.engine import VectorBacktester
from autotrade_lab.strategies import DonchianBreakout

bars = pd.read_csv("ohlcv.csv", index_col=0, parse_dates=True)
result = VectorBacktester(fee_bps=5, slippage_bps=10).run(bars, DonchianBreakout())
print(result.metrics)
```

## Repository map

```text
src/autotrade_lab/
  brokers/       broker-neutral interfaces and guarded adapters
  catalog.py     full hypothesis registry
  engine.py      reproducible baseline backtester
  models.py      instruments and orders
  risk.py        pre-trade portfolio limits
  strategies.py executable signal baselines
docs/
  RESEARCH_CATALOG.md
  SOURCES.md
tests/
```

## Non-negotiable validation rules

- Signals execute one bar later; future data must never enter features.
- Use point-in-time KRX constituents and fundamentals, adjusted prices, delisted assets,
  exchange calendars, taxes, and realistic fills.
- For perpetuals include funding, mark price, liquidation, collateral, and venue failure.
- Report failed variants and apply walk-forward, holdout, and multiple-testing controls.
- Paper trade before real capital. Live adapters require two explicit environment settings;
  broker credentials belong only in local environment variables or a secret manager.

See [the research protocol](docs/RESEARCH_PROTOCOL.md) and
[strategy catalog](docs/RESEARCH_CATALOG.md) for the roadmap.
