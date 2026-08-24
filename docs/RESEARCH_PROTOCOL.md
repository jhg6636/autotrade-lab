# Research protocol

## Pre-data principle: flat hypotheses

Until suitable historical data is collected and audited, no source hierarchy is used. Ideas
from papers, books, broker material, exchange documentation, GitHub, TradingView, blogs,
communities, videos, interviews, and our own observations all enter one flat hypothesis pool.

Source metadata is retained for traceability, not used as a score. Each idea records:

- original URL, title, author or handle, and access date when available;
- source format such as paper, code, post, video, interview, or original observation;
- exact entry, exit, sizing, universe, timeframe, and required data;
- unresolved ambiguity and the least-assumptive baseline interpretation;
- claimed rationale and claimed results, explicitly marked as unverified claims;
- duplicates, variants, and related ideas without choosing a preferred version.

## Inclusion rule

An idea enters the catalog if it can be converted into a falsifiable rule or measurable
hypothesis and does not require illegal, manipulative, deceptive, or unavailable privileged
information. Popularity, credentials, and reported profitability are not inclusion criteria.

## Deduplication without ranking

Similar ideas share a family and canonical mechanism, while parameterizations remain separate
variants. For example, moving-average crossovers, MACD, and Donchian breakouts belong to trend
following but are not collapsed into one result. Duplicate reposts point back to the earliest
source we can locate without increasing the idea's weight.

## When ranking begins

Ranking starts only after the dataset passes point-in-time and quality checks. All implementable
ideas then use the same evaluation pipeline. Decisions are driven by:

1. net out-of-sample performance after realistic costs;
2. drawdown, tail loss, capacity, turnover, and capital lockup;
3. stability across time, assets, regimes, and nearby parameters;
4. data and execution feasibility through supported APIs;
5. operational failure modes and portfolio diversification value.

Source type may help interpret a result but never substitutes for the result.

## Research queue

Discovery proceeds in parallel across source formats and strategy families. Collection should
favor breadth before backtesting: capture the rule faithfully, record variants, and defer
judgment. Only after the first catalog freeze do data acquisition and batch evaluation begin.

For Korean-listed stocks and ETFs, all executable portfolios are long-only. Short-sale rules
may be recorded as historical context but are not implementation candidates. Stock research is
limited to daily and one-minute horizons. Ultra-low-latency strategies remain out of scope. The
Toss Securities Open API now documents both REST and WebSocket interfaces, but that capability
does not establish historical retention, deterministic fill semantics, or suitability for
sub-minute execution.
