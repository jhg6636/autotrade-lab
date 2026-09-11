# Gate E1 eligibility result — NO-GO

- Executed: 2026-09-11 KST, from preparation merge `b4b4705` (PR #30).
- Packet: `gate-e1-eligibility-20260828-v1`.
- Packet SHA-256: `605df1d560b33116823f91033df324876a671cdec51ceb794630009452dd25b6`.
- Terminal manifest SHA-256: `636884299fe5dce7437fee8dedd24b083c81887a86ab7125a8664ba28df91ee6`.
- Local evidence: `research/probes/gate-e1-eligibility-20260828-v1`.

The singular run stopped on request 9, `stock_price_probe_page_1`, with `semantic_ohlcv`.
It attempted 9/24 requests, retained 101 validated rows in eight raw responses (17,499 bytes),
and read 31,391 response bytes. Retries: zero. No remaining slots were attempted.
The canonical terminal manifest and all retained raw responses passed the offline verifier.

| Observation | Result |
| --- | --- |
| 2009 and 2010 listed-instrument boundary | Successful empty responses |
| 2026-08-21 listing pages | 50 + 50 rows; matching totalCount 2,759; zero identity overlap |
| KOSDAQ sentinel | One matching row |
| KODEX 200 listing sentinel | Successful empty response |
| 2009 and 2010 stock-price boundary | Successful empty responses |
| 2026-08-21 stock-price page 1 | HTTP success parsed, OHLCV validation failed |
| Later prices, issuance, dividend slots | Not reached |

The failed response is represented by its byte count and SHA-256 only. Its raw body was deliberately
not retained, so the exact offending prices and whether they represent suspended-trading zeros,
another provider convention, or bad data cannot be determined from this evidence. No such cause is
asserted. Resolving it requires a separately authorized diagnostic packet; this run must never be
repeated. Empty historical samples do not prove that the provider has no history at all.

## Decision

Korean stock daily and ETF daily are both `failed` for this packet; broad collection and backtesting
remain **NO-GO**. The limited listing pagination observation passes, but historical depth, ETF
identity, delisted-stock coverage, corporate actions, and dividends remain insufficient or untested.
Previously documented private noncommercial retention conditions remain the rights baseline; this
run adds no new license permission or data-quality guarantee.

Next user decision: authorize a small stock-price semantic diagnostic, or switch to the independent
crypto eligibility track. No request budget is carried forward automatically.
