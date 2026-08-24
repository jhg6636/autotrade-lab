# Gate D2 Toss observed-contract probe — 2026-08-24

This is a bounded observation of current Toss Open API behavior, not a provider guarantee or a
market-data license. The user authorized the probe after reviewing why documentation alone could
not answer the remaining operational questions.

## Bounds and safety

- OAuth: one client-credentials exchange; credentials and bearer token were not retained.
- Market data: exactly 12 requests, 12 successes, no retries.
- Candles: exactly 800 rows; raw response bodies: 649,329 bytes.
- Endpoints: candles, stock master, stock detail, and KR market calendar only.
- Account, holdings, order, and trade endpoints: not called.
- Raw responses remain local and Git-ignored. The tracked manifest contains parameters, selected
  response headers, counts, checksums, and no credential or bearer-token value.

Manifest SHA-256:
`ab5d48f3ce930238cc3c96e671b5963a15823efdd98484d40afcf830442fde52`.

## Observations

### Pagination

Samsung Electronics (`005930`) was sampled with 100-row adjusted pages.

| Interval | Page 1 cursor | Page 2 first | Page 2 oldest | Cross-page duplicates |
| --- | --- | --- | --- | ---: |
| `1m` | `2026-08-24T14:15:00+09:00` | `2026-08-24T14:15:00+09:00` | `2026-08-24T12:36:00+09:00` | 0 |
| `1d` | `2026-03-27T00:00:00+09:00` | `2026-03-27T00:00:00+09:00` | `2025-10-30T00:00:00+09:00` | 0 |

Both pages were strictly descending. Passing `nextBefore` unchanged selected the next candle, not
an overlapping copy of the prior page's oldest candle, in both observations.

### Historical daily access and adjustment

Two 200-row daily requests used `before=2018-05-10T00:00:00+09:00` around Samsung Electronics'
50-for-1 split breakpoint. Both returned the same 200 timestamps from 2018-05-10 through
2017-07-14.

- Before 2018-05-04, every comparable non-zero-volume row had unadjusted/adjusted price ratio
  exactly `50` and adjusted/unadjusted volume ratio exactly `50`.
- From 2018-05-04 onward, both ratios were `1`.
- The responses included zero-volume daily rows on 2018-04-30, 2018-05-02, and 2018-05-03.

This establishes observed split handling and at least this symbol/date's accessibility. It does not
establish guaranteed retention, dividend treatment, other corporate-action handling, factor
effective-time policy, or revision policy.

### Universe and lifecycle

The four stock-master calls were paced 1.1 seconds apart and all succeeded.

| Market/status | Returned records |
| --- | ---: |
| KOSPI `ACTIVE` | 2,476 |
| KOSPI `DELISTED` | 0 |
| KOSDAQ `ACTIVE` | 1,825 |
| KOSDAQ `DELISTED` | 0 |

Because both delisted snapshots were empty, no delisted symbol could be selected for the one stock
detail call; only active `005930` was requested. These results cannot support a complete historical
point-in-time universe and strengthen the survivorship-bias blocker.

### Historical calendar

The KR calendar accepted `date=2018-05-04`, returned that date as `today`, 2018-05-03 as the prior
business day, and 2018-05-08 as the next business day, with integrated pre-, regular-, and
after-market timestamps. This observes historical calendar access for one date. It does not state
which of those sessions a daily candle aggregates or when that candle is final.

## Contract consequence

The probe narrows uncertainty but does not change the Gate E decision. Five documented-contract
blockers remain:

1. guaranteed `1m` and `1d` retention;
2. point-in-time historical-universe completeness;
3. complete corporate-action methodology and revision policy;
4. daily-candle session scope and completion boundary;
5. local storage and derived-use rights.

Observed facts may guide a later test design, but they must not be promoted to documented provider
guarantees.
