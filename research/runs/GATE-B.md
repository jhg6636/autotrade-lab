# Gate B — execution coverage and first-data decision

Date: 2026-08-24 KST

Status: the user approved the bounded first-data sample for Gate C on 2026-08-24. Approval is
limited to the request, row, storage, endpoint, and safety bounds below.

## Decision summary

Do **not** start bulk market-data collection or backtesting yet. None of the eight target cells has
a source-complete rule with fixed entry, exit/rebalance, sizing, universe, exact timeframe/lag,
required inputs, and exposure. All eight therefore finish this audit as `ambiguous_rule`.

A small read-only capability sample is nevertheless ready for user review. Its purpose is only to
verify provider schemas, pagination, retention, timestamps, missing bars, and local storage—not to
measure strategy performance. It remains a proposal until the user approves Gate B.

This package does not rank strategies or sources. It did not collect market data, use credentials,
call account/order APIs, backtest, promote canonical records, or place orders.

## Audited inventory and evidence boundary

- Local catalog: 35 canonical records and 15 implementation links. Every canonical record still
  has `timeframes=["unknown"]` plus unknown entry, exit, sizing, and required-data placeholders.
- Staging pool: 35 usable LUNA-101 hypotheses. They are all `context_only`; none is a complete
  executable Korean application. The only usable crypto-perpetual record uses one-minute/weekly
  context, outside the selected 1-hour/4-hour and daily cells.
- One bounded gap pass inspected 12 unique public sources: six Korean and six crypto. The immutable
  review packets are identified by SHA-256 in `LUNA-201-203.md`. No second pass is authorized.
- No new source satisfied the complete admission contract. One 1-hour BTC perpetual script was
  close enough to inspect, but its mutable version page, fill convention, costs/funding, and
  tuned-rule provenance remain unresolved.

## Eight-cell coverage matrix

The state is the dominant feasibility blocker, not a profitability judgment.

| Cell | Exact local scaffold inspected | Bounded source result | Final state | Blocking fact |
| --- | --- | --- | --- | --- |
| Korean equity / daily | `VolatilityBreakout(k=0.5)` | 3 inspected; 0 complete | `ambiguous_rule` | No source binds a complete long-only daily rule to the scaffold. |
| Korean equity / 1 minute | `VolatilityBreakout(k=0.5)` | 2 inspected; 0 complete | `ambiguous_rule` | No exact one-minute rule, bar-close/fill lag, or source sizing. |
| Korean ETF / daily | `VolatilityBreakout(k=0.5)` | 1 inspected; 0 complete | `ambiguous_rule` | Provider scope exists, but no complete ETF strategy rule was found. |
| Korean ETF / 1 minute | `VolatilityBreakout(k=0.5)` | 3 inspected; 0 complete | `ambiguous_rule` | “Intraday” evidence does not establish one-minute parameters or timing. |
| Crypto spot / 1 hour | `VolatilityBreakout(k=0.5)` | 0 assigned; 0 complete | `ambiguous_rule` | Sources omit either explicit spot instrument type or complete sizing/exit. |
| Crypto spot / daily | `VolatilityBreakout(k=0.5)` | 0 assigned; 0 complete | `ambiguous_rule` | Daily VMA evidence omits explicit spot type, sell predicate, sizing, and lag. |
| Crypto perpetual / 1 hour | `TimeSeriesMomentum(lookback=126, deadband=0)` | 1 assigned; 0 complete | `ambiguous_rule` | The inspected 1-hour script is a different, mutable multi-filter rule with unresolved fills/costs. |
| Crypto perpetual / daily | `TimeSeriesMomentum(lookback=126, deadband=0)` | 0 assigned; 0 complete | `ambiguous_rule` | No inspected source states a complete daily perpetual rule. |

The scaffolds above are code/data-shape probes, not admitted research candidates. Choosing them does
not fill a coverage cell or promote a canonical record.

## Retained scaffold feasibility metadata

### Long-only volatility-breakout scaffold

Applies only as a data-shape probe to the four Korean cells and two crypto-spot cells.

- Exact code rule: at bar `t`, compute prior range `high[t-1]-low[t-1]` and trigger
  `open[t] + 0.5 * prior_range`; target exposure is `1` when `close[t] > trigger`, otherwise `0`.
- Required fields: chronological OHLCV. The implementation validates all five fields even though
  the calculation uses OHLC. Minimum warm-up is two bars.
- Timing ambiguity: the target uses the same bar's close and therefore cannot be filled at that
  same close without a separately specified execution convention. A later experiment must lag the
  target or define an executable close auction rule.
- Korean constraints: exposure already lies in `[0,1]`; no stock or ETF short sale is used.
- Point-in-time needs: dated active/delisted universe snapshots, listing and suspension state,
  market calendar/session, security type, and stable symbol identifiers.
- Corporate actions: retain raw observations and provider adjustment flags; do not mix adjusted
  daily candles with unadjusted intraday data without a documented factor policy.
- Timezones: Korean bars in KST with KRX/NXT session identity; crypto bars normalized to UTC while
  preserving venue timestamps and requested candle timezone.
- Retention/license: unresolved until a read-only capability probe and terms review. Public API
  availability is not permission to redistribute raw data.
- State: `ambiguous_rule` in all six cells because timeframe, fill convention, universe, and
  source-to-code binding are not complete.

### Signed time-series-momentum scaffold

Applies only as a data-shape probe to the two crypto-perpetual cells.

- Exact code rule: compute `close[t] / close[t-126] - 1`; target `+1` if positive, `-1` if
  negative, else `0`. The default deadband is zero.
- Required fields: chronological OHLCV under the shared validator; calculation uses close. Minimum
  warm-up is 127 bars.
- Execution needs: contract metadata, mark/index price policy, funding timestamps and cash flows,
  fee tier, tick/lot sizes, margin/leverage, liquidation state, and a next-bar fill convention.
- Point-in-time needs: dated contract lifecycle/status and symbol mapping. Perpetual funding and
  open-interest series must be aligned using their publication timestamps rather than backfilled.
- Timezone: store exchange epoch timestamps in UTC and record candle boundary, funding interval,
  and any venue-specific daily cutoff.
- Retention/license: Binance public endpoints are provider candidates, but historical depth,
  regional availability, and redistribution terms require confirmation for the selected account
  jurisdiction. Archive files, if later considered, need their own license/provenance record.
- State: `ambiguous_rule` for 1-hour and daily because no complete source binds this scaffold to
  those exact perpetual cells.

## Provider and data matrix

| Provider | Cells | Documented surface relevant to the proposal | Access/API estimate | Remaining feasibility issues |
| --- | --- | --- | --- | --- |
| Toss Securities | Korean equity/ETF, daily/1m | OAuth market data; `GET /api/v1/candles` supports `1m` and `1d`, max 200, `before` pagination, adjusted default `true`; full-market stock master can filter `ETF` and `DELISTED`; KRX/NXT calendar; REST plus WebSocket | Market data requires an OAuth token but not an account header. Chart group is documented up to 20 TPS and stock-all up to 1 TPS; response headers are authoritative. | Allowed-IP setup, historical retention, delisted-history completeness, adjustment-factor semantics, redistribution terms, and practical KRX/NXT bar coverage are not documented sufficiently. |
| KRX Data Marketplace | Korean equity/ETF | Official stock and ETP catalog plus historical/feed/license surfaces | No calls proposed in the first sample. Treat paid/download products as a separate user decision. | Exact product, price, point-in-time history, minute depth, license, and redistribution rights unresolved. |
| Upbit | Crypto spot, 1h/4h/daily | Public minute candles include 60m and 240m; daily candles; max 200 per request; candle group up to 10 requests/s/IP | Four public calls in the proposed sample, 200 rows each. | Global documentation is region-specific; Korean endpoint/policy, symbol lifecycle, retention, terms, and redistribution must be verified. Missing candles are expected when no trades occur. |
| Binance Spot | Crypto spot, 1h/4h/daily | Public `GET /api/v3/klines`; 1h, 4h, and 1d; max 1,000; configurable candle timezone with UTC request bounds | Four public calls in the proposed sample, 1,000 rows each. | Regional availability/terms, symbol lifecycle, missing data, daily cutoff, and redistribution require review. |
| Binance USDⓈ-M | Crypto perpetual, 1h/4h/daily | Public perpetual klines plus funding-rate, mark/index price, exchange info, and open-interest surfaces | Four kline calls in the proposed sample; metadata/funding probes counted separately only after endpoint-level review. | Funding/open-interest history limits, contract lifecycle, regional availability/terms, and redistribution require review. |

Official capability references reviewed: [Toss overview](https://openapi.tossinvest.com/openapi-docs/overview.md),
[Toss market-data API](https://openapi.tossinvest.com/openapi-docs/latest/api-reference/Apis/MarketDataApi.md),
[Toss stock-info API](https://openapi.tossinvest.com/openapi-docs/latest/api-reference/Apis/StockInfoApi.md),
[Upbit minute candles](https://global-docs.upbit.com/reference/list-candles-minutes),
[Upbit daily candles](https://global-docs.upbit.com/reference/list-candles-days), and
[Binance API documentation](https://developers.binance.com/en/docs/catalog).

## Point-in-time and storage contract

Any later collector must keep three layers:

1. immutable raw response plus request parameters, response headers, retrieval time, provider,
   checksum, and documented endpoint/version;
2. normalized bars/metadata with explicit venue, instrument type, timezone, interval, adjustment
   state, and missing-bar reason;
3. point-in-time snapshots for universe membership, listing status, warnings, calendars, contract
   status, and corporate-action factors.

Never forward-fill a missing crypto candle as a real trade bar. Never reconstruct a past Korean
universe from today's active list. Duplicate keys are `(provider, venue, symbol, instrument_type,
interval, open_time, adjustment_state)` and conflicting duplicates must stop normalization.

## Proposed bounded first-data sample

This sample was approved for Gate C within the stated bounds. It combines the future LUNA-301 Toss
capability probe and LUNA-303 crypto public-data probe; it does not authorize LUNA-302 universe
history or any backtest.

### Scope

- Toss: Samsung Electronics `005930`, SK hynix `000660`, KODEX 200 `069500`, and KODEX KOSDAQ150
  `229200`; latest 200 daily and latest 200 one-minute candles per symbol, plus one KOSPI and one
  KOSDAQ/ETF-capable stock-master query and one Korean market-calendar query. Request both adjusted
  and unadjusted daily bars only for one symbol to inspect semantics. No account header.
- Upbit: `KRW-BTC` and `KRW-ETH`; latest 200 60-minute and 200 daily candles per symbol using the
  verified Korean quotation endpoint only.
- Binance: spot and USDⓈ-M perpetual `BTCUSDT` and `ETHUSDT`; latest 1,000 1-hour and 1,000 daily
  klines per instrument. Add only the minimal public exchange-info/funding metadata needed to audit
  lifecycle and timestamps; no private endpoint.

### Upper-bound estimate

| Item | Bound |
| --- | ---: |
| Candle requests | 9 Toss + 4 Upbit + 8 Binance = 21 |
| Metadata/calendar requests | at most 8 |
| Total HTTP requests excluding OAuth token issuance | at most 29 |
| Candle rows | at most 10,600 |
| Raw JSON plus normalized Parquet and manifests | budget 25 MB |
| Direct data purchase | KRW 0; stop if any term, entitlement, or paid product is required |

The 25 MB budget intentionally allows large raw envelopes and duplicated adjusted/unadjusted
inspection. Actual compressed storage should be much smaller. The sample stops after these bounds
even if retention is shorter or a cell remains unresolved.

## Stop and acceptance criteria for the next gate

The sample may start only after explicit user approval and, for Toss, credentials supplied through
an approved secret mechanism. It must stop before account/holding/order endpoints, license
acceptance, payment, CAPTCHA/access-control bypass, broader pagination, backtesting, or trading.

Gate C should be considered only if the sample demonstrates:

- reproducible raw checksums and idempotent normalization;
- explicit timestamps/timezones and no unexplained duplicate or missing bars;
- observed retention and rate-limit headers recorded without extrapolation;
- ETF/security-type and perpetual/spot identity preserved;
- corporate-action and point-in-time gaps reported rather than imputed;
- user review of provider terms and any redistribution restriction.

Strategy-rule ambiguity remains a separate track. A successful data probe does not turn any of the
eight cells into an admitted or profitable strategy.

## Unresolved ambiguity register

1. No complete source-to-code binding for any of the eight cells.
2. Same-bar close signals lack an executable fill convention.
3. Toss historical retention, adjustment factors, delisted coverage, and redistribution terms are
   not established by documentation alone.
4. KRX/NXT consolidated versus venue-specific bar semantics need an observed schema probe.
5. Korean point-in-time membership and corporate-action history may require an external or paid
   source; no license will be accepted implicitly.
6. Upbit Korean-region endpoint policy and historical retention require verification.
7. Binance regional availability, lifecycle completeness, funding/open-interest retention, and
   redistribution terms require verification.
8. The inspected TradingView perpetual script is mutable and omits a complete live cost/fill model;
   its reported results remain unverified and unranked.
