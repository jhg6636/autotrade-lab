# autotrade-lab

A multi-asset laboratory for researching systematic strategies across Korean-listed stocks,
ETFs, and crypto markets. The project separates research, simulation, paper trading, risk,
and live execution so a promising backtest cannot accidentally become a real order.

> This is research software, not investment advice. No strategy is assumed profitable.
> Live trading is disabled by default.

## 프로젝트 진행 상황

**현재 위치:** Gate E1-PREP을 완료했습니다. 금융위원회 공공데이터포털의 국내 주식 일봉
데이터에 대해 첫 번째 제한적 실현 가능성 검증을 실행하기 직전입니다. 국내 주식 과거
백테스트, 모의투자, 실거래는 아직 시작하지 않았습니다.

```mermaid
flowchart LR
    A["연구 기반<br/>완료"] --> B["평탄화 전략 조사<br/>일부 완료"]
    B --> C["실행 가능성·데이터 계약<br/>완료"]
    C --> D["국내 데이터 소스 검증<br/>E1-PREP 완료"]
    D --> E["E1-DATA 제한 검증<br/>승인 대기"]
    E --> F["과거 데이터셋·품질 검증<br/>미시작"]
    F --> G["백테스트·강건성 검증<br/>미시작"]
    G --> H["모의투자<br/>미시작"]
    H --> I["소액 실거래 파일럿<br/>미시작"]

    classDef done fill:#d8f3dc,stroke:#2d6a4f,color:#081c15;
    classDef partial fill:#fff3bf,stroke:#b08900,color:#3d2f00;
    classDef current fill:#dbeafe,stroke:#2563eb,color:#172554,stroke-width:3px;
    classDef future fill:#f3f4f6,stroke:#9ca3af,color:#374151;
    class A,C done;
    class B partial;
    class D,E current;
    class F,G,H,I future;
```

[전체 마일스톤 대시보드](docs/ROADMAP.html)에서 완료 근거, 중단 게이트, 앞으로 남은 단계를
확인할 수 있습니다. 정확한 현재 작업은 [활성 핸드오프](research/runs/HANDOFF.md)를 기준으로
판단합니다.

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
