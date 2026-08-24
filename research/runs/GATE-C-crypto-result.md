# Gate C Phase 1 result — public crypto candles

Date: 2026-08-24 UTC/KST

## Outcome

The bounded public-crypto data path is technically suitable for **limited follow-up collection**.
This is a plumbing result, not a strategy or profitability result. Perpetual strategy evaluation is
not data-ready from candles alone because funding, mark/index prices, contract lifecycle, fees,
margin, and liquidation fields remain outside this sample.

## Budget and provenance

- 12 configured public requests; 12 attempted exactly once; 12 HTTP 200 responses;
- 8,800 returned and normalized rows, exactly the Phase 1 maximum;
- 1,628,753 raw-response bytes and 1,963,244 bytes for the full local artifact set;
- no credentials, API keys, signatures, account headers, private endpoints, or retries;
- manifest SHA-256:
  `7ae502ba69a0305a72fa88d4c4e5d2572ed55c7032ac9ba5a116b204517dbbc7`;
- Parquet SHA-256:
  `9a9d59f2dce69edce8d840309b079bb5b546dc665635b6d456ec0c6c4489fe10`;
- PyArrow version `23.0.1`; two independent normalizations of the same raw inputs were
  byte-identical.

Raw bodies and normalized market values remain local and Git-ignored pending a provider-terms and
redistribution decision. The committed manifest contains request metadata and response checksums;
the committed quality report contains aggregate coverage and structural results.

## Observed coverage

| Provider/market | Symbols | Interval | Rows each | Earliest returned | Latest returned |
| --- | --- | --- | ---: | --- | --- |
| Upbit Korea spot | KRW-BTC, KRW-ETH | 1h | 200 | 2026-08-15 21:00 UTC | 2026-08-24 04:00 UTC |
| Upbit Korea spot | KRW-BTC, KRW-ETH | 1d | 200 | 2026-02-06 00:00 UTC | 2026-08-24 00:00 UTC |
| Binance spot | BTCUSDT, ETHUSDT | 1h | 1,000 | 2026-07-13 13:00 UTC | 2026-08-24 04:00 UTC |
| Binance spot | BTCUSDT, ETHUSDT | 1d | 1,000 | 2023-11-29 00:00 UTC | 2026-08-24 00:00 UTC |
| Binance USDⓈ-M perpetual | BTCUSDT, ETHUSDT | 1h | 1,000 | 2026-07-13 13:00 UTC | 2026-08-24 04:00 UTC |
| Binance USDⓈ-M perpetual | BTCUSDT, ETHUSDT | 1d | 1,000 | 2023-11-29 00:00 UTC | 2026-08-24 00:00 UTC |

These bounds prove only the returned page depth. No request attempted to discover maximum provider
retention, and no deeper-retention claim is made.

## Quality audit

Across the 12 provider/symbol/interval datasets:

- duplicate identity keys: 0;
- missing intervals inside each returned page: 0;
- non-grid deltas and off-grid open times: 0;
- invalid OHLC relationships: 0;
- non-finite numeric rows: 0;
- negative base/quote volume rows: 0;
- incomplete rows: 12, exactly one current in-progress candle per dataset.

The normalized key preserves provider, venue, instrument type, symbol, interval, UTC open time, and
adjustment state. Spot and perpetual BTCUSDT are therefore not conflated. The current incomplete
candle must be excluded or snapshotted separately in any later research dataset.

Observed headers showed Upbit `Remaining-Req` values in the candle group and Binance used-weight
headers. They prove only per-response observations; the collector does not turn them into a fixed
quota assumption.

## Gate C interpretation

- Upbit spot hourly/daily candles: limited collector capability passes.
- Binance spot hourly/daily candles: limited collector capability passes.
- Binance USDⓈ-M hourly/daily candles: candle capability passes, but a perpetual implementation
  remains `needs_external_data` for funding, mark/index, contract metadata, fees, and margin risk.
- Provider retention beyond one page, symbol lifecycle history, delisting behavior, and raw-data
  redistribution rights remain unresolved.
- Toss Phase 2 remains paused until credentials are supplied through an approved secret mechanism.

For the small-capital/high-upside persona, this sample says nothing about attainable returns. The
next research gate must explicitly model minimum notional, tick/lot rounding, fees, spread, turnover,
capital-at-risk, drawdown stop, and probability of ruin before comparing returns.
