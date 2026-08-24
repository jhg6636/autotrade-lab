# autotrade-lab

A multi-asset laboratory for researching systematic strategies across Korean-listed stocks,
ETFs, and crypto markets. The project separates research, simulation, paper trading, risk,
and live execution so a promising backtest cannot accidentally become a real order.

> This is research software, not investment advice. No strategy is assumed profitable.
> Live trading is disabled by default.

## Project status

**Current position:** Gate E1-PREP is complete. The project is waiting immediately before the
first bounded feasibility call to the official Korean daily stock-data sources. No Korean
historical backtest, paper trade, or live trade has started.

```mermaid
flowchart LR
    A["Research foundation<br/>complete"] --> B["Flat discovery<br/>partial"]
    B --> C["Feasibility & data contracts<br/>complete"]
    C --> D["Korean source qualification<br/>E1-PREP complete"]
    D --> E["E1-DATA bounded probe<br/>awaiting approval"]
    E --> F["Historical dataset & QA<br/>not started"]
    F --> G["Backtest & robustness<br/>not started"]
    G --> H["Paper trading<br/>not started"]
    H --> I["Small-capital live pilot<br/>not started"]

    classDef done fill:#d8f3dc,stroke:#2d6a4f,color:#081c15;
    classDef partial fill:#fff3bf,stroke:#b08900,color:#3d2f00;
    classDef current fill:#dbeafe,stroke:#2563eb,color:#172554,stroke-width:3px;
    classDef future fill:#f3f4f6,stroke:#9ca3af,color:#374151;
    class A,C done;
    class B partial;
    class D,E current;
    class F,G,H,I future;
```

Open the [full milestone dashboard](docs/ROADMAP.html) for completed evidence, stop gates, and the
remaining path. The [active handoff](research/runs/HANDOFF.md) remains the source of truth for the
exact current action.

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
  AGENT_WORKFLOW.md
  DISCOVERY_PR_WORKFLOW.md
  RESEARCH_CATALOG.md
  RESEARCH_PROTOCOL.md
  SOURCES.md
research/runs/
  HANDOFF.md    active objective and cross-device resume state
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

Agents and contributors should start with [AGENTS.md](AGENTS.md) and the
[active handoff](research/runs/HANDOFF.md). See [the research protocol](docs/RESEARCH_PROTOCOL.md),
[agent workflow](docs/AGENT_WORKFLOW.md), and [strategy catalog](docs/RESEARCH_CATALOG.md) for the
roadmap and operating constraints.
