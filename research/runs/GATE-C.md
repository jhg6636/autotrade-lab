# Gate C — bounded first-data capability probe

- Starting main commit: `b9c8d57448c29d9739551d813cf3e1be2b13620b`
- Working branch: `agent/GATE-C-capability-probe`
- Stage: Phase 1 merged; Toss Phase 2 collector verified and awaiting local credentials

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

Phase 2 remains paused until the user supplies Toss credentials through an approved secret
mechanism. It may use only OAuth and public-equivalent market-data/stock-info/calendar endpoints
defined in `research/runs/GATE-B.md`. Account, asset, holding, buying-power, commission, conditional
order, and order endpoints are forbidden. The combined Phase 1 and Phase 2 totals must remain within
the hard budget.

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

## Next action

Wait for the user to confirm a local mode-0600 `.env.toss` and Toss allowed-IP registration; do not
make a Toss request before both confirmations.
