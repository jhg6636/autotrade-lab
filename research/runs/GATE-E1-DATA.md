# Gate E1-DATA — Korean daily-data feasibility run

- Base commit: `1dfc2c7`
- Working branch: `agent/GATE-E1-DATA`
- User approval: 2026-08-26 KST
- Plan SHA-256:
  `ae802b8d4245a153af5abea3e2875049ee086e6556541ff3f8f1a5d2677198f0`
- Stage: executed once; stopped on first-slot transport failure

## Fixed boundary

Execute exactly the 24 slots in `gate_e1_request_plan()` once: at most 1,200 rows, 5 MiB of raw
responses, and zero retries. Use only the four admitted Financial Services Commission publications
and the six allowlisted read-only operations. Do not replace an empty or failed slot, reuse unused
budget, expand pagination, call a brokerage API, backtest, rank, optimize, access an account, order,
or trade.

The service key must be the decoded Public Data Portal key stored locally in a regular non-symlink
`.env.public-data` file with mode `0600`. Never print the key, the live URL, or an exception context
containing the URL. The file and raw bodies remain Git-ignored.

## Preflight

- [x] PR `#23` merged into `main` as `1dfc2c7`.
- [x] E1-DATA branch created from that merge.
- [x] Runtime request-plan hash matches the approved SHA-256.
- [x] `.env.public-data` is covered by `.gitignore`.
- [x] User applied for all four admitted APIs; the portal showed all four as approved.
- [x] Mode-`0600` `.env.public-data` existed and passed `load_public_data_service_key()` without
  printing the credential.
- [x] Output directory `research/probes/gate-e1-korean-daily-20260826` did not exist before the
  singular execution.

## Singular execution

Run only after every preflight item passes:

```bash
.venv/bin/python - <<'PY'
from pathlib import Path

from autotrade_lab.gate_e1_prep import (
    collect_gate_e1_data,
    load_public_data_service_key,
)

key = load_public_data_service_key(Path(".env.public-data"))
try:
    collect_gate_e1_data(
        Path("research/probes/gate-e1-korean-daily-20260826"),
        decoded_service_key=key,
        approved_plan_sha256=(
            "ae802b8d4245a153af5abea3e2875049ee086e6556541ff3f8f1a5d2677198f0"
        ),
    )
finally:
    del key
PY
```

Do not rerun this command after any request is attempted. A failure is an E1 observation and stop
condition, not authorization to retry.

## Execution result

The singular command was executed at 2026-08-26 16:15 KST. The first approved slot,
`listing_2009_boundary`, reached the transport open step and failed with the collector's redacted
`network or transport failure; stop without retry` condition. The collector stopped immediately.
It did not retain a response body or create a manifest, and no further slot was attempted.

- local slot attempts: 1 of 24;
- confirmed HTTP responses: 0;
- retained raw files, rows, and response bytes: 0;
- retries: 0;
- output state: an empty local `raw/` directory only;
- credential material retained in artifacts or logs: false;
- whether the failed connection reached the provider: not observed.

The failure cannot be treated as evidence about provider history, schema, pagination, or data
quality. It is an operational Gate failure. The approved plan forbids rerunning the command after an
attempt, so any recovery must use a separately reviewed and approved plan rather than silently
retrying this run.

## Required post-call evidence

| Dimension | Required observation | Status |
| --- | --- | --- |
| Manifest integrity | canonical manifest reproduces local raw checksums, bytes, rows, order, plan, and limits | `failed`: no response or manifest |
| Historical boundary | listing and stock-price presence/absence for 2009-12-31 and 2010-01-04 | `not_observed` |
| Pagination | stable metadata and no duplicate identity across each preselected page pair | `not_observed` |
| KOSDAQ identity | explicit returned identity for short code `196170` | `not_observed` |
| ETF daily | explicit KODEX 200 ISIN/security identity at the old and probe dates | `not_observed` |
| Samsung split | pre/post-split raw OHLCV plus issuance fields, without inferred adjustment semantics | `not_observed` |
| Delisted stock | Hanjin Shipping price and issuance records joined by returned stable identifiers, with `lstgAbolDt=20170307` | `not_observed` |
| Dividends | returned record/payment dates and share class joined through returned identifiers | `not_observed` |
| Provider behavior | safe quota headers, exact row/byte totals, and any no-retry error | `failed`: redacted transport stop; no headers |
| Unobserved semantics | halts, corrections, code changes, and withdrawals remain `not_observed` unless directly present | `not_observed` |

## Required decisions

Assign Korean stock daily and Korean ETF daily separately as `feasible_for_E2`, `limited`, or
`failed`. A successful HTTP response is insufficient. Silent current-date substitution, incorrect
identity/date, duplicate pagination, a missing fixed delisted sample, absent explicit ETF identity,
schema/authentication/429 errors, or a failed raw verifier prevents an unconditional GO.

## Decision and stop record

- Korean stock daily: `failed` for Gate E1-DATA; broad historical collection remains NO-GO.
- Korean ETF daily: `failed` for Gate E1-DATA; broad historical collection remains NO-GO.

This decision reflects missing evidence, not a judgment that the official publications are
intrinsically unusable. The stop condition is the first-slot transport failure under a zero-retry
plan. The next consequential action is to design a new, minimal connectivity-recovery packet with a
new approval hash; do not reuse this run directory or rerun the approved command.
