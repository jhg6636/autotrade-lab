# Gate C Toss market-data sample — 2026-08-24

This directory records the bounded Toss market-data capability probe. It is evidence about data
plumbing, not evidence of strategy profitability or readiness to trade.

## Observed result

- OAuth issuance: 1 successful request; client credentials and bearer token were not persisted.
- Market-data requests: 15 attempted, 12 successful, 3 rate-limited (`HTTP 429`).
- Candles: all 9 planned requests succeeded, producing 1,800 normalized rows across Samsung
  Electronics, SK hynix, KODEX 200, and KODEX KOSDAQ 150 at `1d` and `1m`; Samsung daily data was
  sampled both adjusted and unadjusted.
- Reference data: active KOSPI master, four selected security details, and the KR market calendar
  succeeded. KOSPI delisted, KOSDAQ active, and KOSDAQ delisted masters were rate-limited.
- Combined Gate C: 27/29 market-data requests and 10,600/10,600 candle rows.
- Structural candle checks: pass, with zero identity duplicates, invalid OHLC rows, non-finite
  numeric rows, negative volumes, off-grid timestamps, or same-session non-grid deltas.
- Gate D correction: the canonical OpenAPI confirms `timestamp` is the interval start. The 800
  one-minute rows have fixed one-minute completion bounds (8 were in progress at retrieval), while
  all 1,000 daily rows retain null close/completion because candle-to-session scope is undocumented.

The three failed stock-master calls were not retried because only two requests remained in the hard
budget. The collector now paces consecutive `/stocks/all` calls by 1.1 seconds for future runs.

## Deterministic artifacts

- `manifest.json`: request metadata, statuses, selected response headers, sizes, and raw checksums;
  SHA-256 `c9e4c92e473557c62baab6ec9c7b31e9060dfb62fb443a0892aabe673ad02a48`
- `quality_report.json`: normalized coverage, quality findings, failed reference calls, and unresolved
  semantics/licensing statements; SHA-256
  `fae565a98dc02294a40ce8562c481e654044730d9adce799bb93c7e93f0993a4`
- local `normalized/candles.parquet`: 1,800 rows; SHA-256
  `1069360f6694126fae5246c09969b30932c00d62b6d5b4c6914c095da475da25`

Raw bodies and Parquet are intentionally Git-ignored. Authenticated access does not establish
redistribution rights. Daily session completion, historical retention, and point-in-time universe
completeness remain unresolved and must be reviewed before backtesting.
