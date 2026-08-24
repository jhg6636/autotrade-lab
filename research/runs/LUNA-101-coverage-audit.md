# LUNA-101 coverage closeout audit

- Audited integration commit: `ce392baacccc37bc57a56391578844d0bd425d52`
- Audit mode: local deterministic ledger inspection only; no web collection or model delegation
- Decision: the fixed 80-usable-source quota is retired; LUNA-101 closes on hypothesis breadth,
  source linkage, documented coverage, and validation

## Completion result

- Sources: 80 total — 26 usable, 53 incomplete, 1 inaccessible.
- Hypotheses: 95 total — 35 usable, 60 incomplete.
- All 35 usable hypotheses have at least one source reference.
- All source references from usable hypotheses resolve to existing usable source records.
- Canonical records modified: false.
- Automatic relation merge: false.
- Deterministic aggregate SHA-256:
  `f5f7213dc5a1abcb4b240eff748ed898b69145a16876327b9d82f2744e115fe9`.
- Validation: two byte-identical aggregate runs, committed-report equality, 35/35 usable source-link
  audit, 84 passing tests, and clean Ruff check/format and diff checks.

The 30-usable-hypothesis breadth floor is satisfied. Source count remains a descriptive provenance
metric, not a completion quota. Additional sources are justified only by a later explicit gap-driven
request, not by a raw count.

## Usable-hypothesis coverage

### Family

| Family | Count |
| --- | ---: |
| time_series_momentum | 12 |
| cross_sectional_momentum | 4 |
| currency_carry | 3 |
| currency_momentum | 3 |
| merger_arbitrage | 2 |
| seasonality | 2 |
| trend_following | 2 |
| volatility_management | 2 |
| mean_reversion | 1 |
| oscillator | 1 |
| pairs_trading | 1 |
| risk_parity | 1 |
| volatility_breakout | 1 |

### Market

| Market | Count |
| --- | ---: |
| multi_asset | 27 |
| us_equity | 7 |
| crypto_perp | 1 |

### Timeframe tags

Timeframes are multi-valued, so these counts do not sum to 35.

| Timeframe | Count |
| --- | ---: |
| monthly | 19 |
| daily | 17 |
| 15-second | 3 |
| 30-second | 3 |
| 60-second | 3 |
| weekly | 2 |
| one_minute | 1 |

### Direction and scope

| Dimension | Count |
| --- | ---: |
| long_short | 32 |
| long_only | 3 |
| context_only | 35 |

## Documented limitations

- The pool is concentrated in time-series momentum (12/35) and multi-asset research (27/35).
- US equities have seven usable hypotheses; crypto perpetuals have one.
- All 35 records are research context only. Executability and broker/data availability are later
  audits, not implied by `usable` discovery status.
- Korean-market breadth is intentionally outside LUNA-101 and belongs to LUNA-104.
- Empty or sparse cells are recorded as limitations. They do not automatically authorize another
  discovery batch.

## Closeout rule

LUNA-101 discovery is complete when this audit, source/reference validation, deterministic aggregate,
test/lint checks, integration tracker, and umbrella PR agree. Further collection requires a new,
explicitly named coverage gap and a bounded request. No generic source-count chase remains.

LUNA-101-06 was stopped before normalization review, commit, or PR when the completion gate changed.
Its two planning commits remain isolated on `agent/LUNA-101-06-complete-rule-batch`; partial local
normalization was preserved in stash `aborted LUNA-101-06 partial normalization` and contributes
nothing to the counts above. Do not resume it without an explicit user request naming a coverage gap.
