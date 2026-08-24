# Gate C — bounded first-data capability probe

- Phase 2 base commit: `b790a2dc770f1b7eace8179e802b9430e4710c09`
- Working branch: `agent/GATE-C-toss-probe`
- Stage: Phase 1 merged; Phase 2 collected, normalized, and reviewed in PR `#19`

## Objective

Execute the user-approved Gate B sample to learn whether public crypto and Toss market-data
surfaces can support reproducible, point-in-time-aware collection. This run tests data plumbing,
not strategies or profitability. The investor context is `docs/INVESTOR_PROFILE.md`.

## Hard budget

- at most 29 HTTP market-data requests, excluding one future Toss OAuth token issuance;
- at most 10,600 candle rows;
- at most 25 MB across raw responses, normalized data, manifests, and reports;
- no retry may occur without counting as another request;
- stop when any bound would be exceeded.

## Phase 1 — public crypto sample

Exactly 12 requests and at most 8,800 rows:

| Provider | Instrument | Symbols | Intervals | Rows/request | Requests |
| --- | --- | --- | --- | ---: | ---: |
| Upbit Korea | spot | `KRW-BTC`, `KRW-ETH` | `60m`, `1d` | 200 | 4 |
| Binance | spot | `BTCUSDT`, `ETHUSDT` | `1h`, `1d` | 1,000 | 4 |
| Binance USDⓈ-M | perpetual | `BTCUSDT`, `ETHUSDT` | `1h`, `1d` | 1,000 | 4 |

Only public quotation endpoints are allowed. No API key, account header, signature, private endpoint,
or order surface may be read or called. Each configured request is attempted once. A provider error
is a capability result and is not bypassed by changing regions, mirrors, or instruments.

## Phase 2 — Toss sample

Phase 2 used one OAuth issuance and exactly 15 public-equivalent market-data/stock-info/calendar
requests defined in `research/runs/GATE-B.md`. Account, asset, holding, buying-power, commission,
conditional-order, and order endpoints were not called. Nine candle calls and three reference calls
succeeded; three consecutive stock-master calls returned `HTTP 429`. They were not retried because
only two requests remained in the combined hard budget.

## Artifact contract

Every attempted request records provider, public URL and parameters, attempt ordinal, retrieval
time, HTTP status, selected rate-limit/date/content headers, byte length, and response SHA-256.
Successful response bodies are immutable raw JSON. Error bodies are preserved with the same size
and secret checks.

Normalized candles use an explicit schema containing provider, venue, instrument type, symbol,
interval, UTC open/close time, OHLCV, quote volume when available, trade count when available,
completion state, adjustment state, and raw-response SHA-256. Rows are sorted by their full identity
key before deterministic Parquet output.

The quality report must include request/row/byte budgets, coverage bounds, duplicate keys, missing
intervals, incomplete latest candles, parse failures, response headers, and unresolved retention or
licensing questions. Re-normalizing the same raw inputs twice must produce byte-identical Parquet
and report artifacts.

## Stop conditions

Stop before using credentials in Phase 1, reading environment secrets not explicitly requested,
calling private/account/order APIs, accepting terms, paying for data, bypassing regional or access
controls, expanding symbols/history, retrying beyond the budget, backtesting, ranking, optimizing,
promoting canonical records, or trading.

## Completion

Gate C is complete when the bounded artifacts and deterministic collector/normalizer pass tests and
coordinator review, the report distinguishes observed facts from unknown retention/licensing terms,
the reviewed PR is merged, and HANDOFF recommends whether broader collection should proceed. A
successful capability probe makes no strategy profitable or executable by itself.

## Phase 2 result

- OAuth: success; client credentials and bearer token were not persisted.
- 15 market-data requests attempted, 12 successful, 3 rate-limited; all 9 candle requests succeeded.
- 1,800 Toss candles normalized; combined Gate C totals are 27 requests and 10,600 candle rows.
- Structural candle quality passed. Korean daily calendar gaps were not inferred without a
  point-in-time session calendar; intraday gap checks exclude cross-session boundaries.
- Toss Parquet regeneration is byte-identical at SHA-256
  `93e091692e181e80a55de02a7f0361dd33bf870262ba88184ddcfe2939966e38`.
- Raw bodies and Parquet remain local/Git-ignored because redistribution rights are unresolved.
- The collector now paces consecutive `/stocks/all` calls; the three failed calls remain preserved
  as capability evidence and were not retried.

## Next action

Merge reviewed PR `#19`. Then plan a documentation-first Gate D that resolves Toss timestamp meaning,
historical retention, point-in-time universe support, and redistribution terms before authorizing any
broader collection. Do not spend the two remaining request slots, backtest, rank, promote, or trade.
