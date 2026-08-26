# Gate E1-DATA — Korean daily-data feasibility run

- Base commit: `1dfc2c7`
- Working branch: `agent/GATE-E1-DATA`
- User approval: 2026-08-26 KST
- Plan SHA-256:
  `ae802b8d4245a153af5abea3e2875049ee086e6556541ff3f8f1a5d2677198f0`
- Stage: approved; waiting for local Public Data Portal key

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
- [ ] User applied for all four admitted APIs.
- [ ] Mode-`0600` `.env.public-data` exists and passes `load_public_data_service_key()`.
- [ ] Output directory `research/probes/gate-e1-korean-daily-20260826` does not exist.

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

## Required post-call evidence

| Dimension | Required observation | Status |
| --- | --- | --- |
| Manifest integrity | canonical manifest reproduces local raw checksums, bytes, rows, order, plan, and limits | `pending` |
| Historical boundary | listing and stock-price presence/absence for 2009-12-31 and 2010-01-04 | `pending` |
| Pagination | stable metadata and no duplicate identity across each preselected page pair | `pending` |
| KOSDAQ identity | explicit returned identity for short code `196170` | `pending` |
| ETF daily | explicit KODEX 200 ISIN/security identity at the old and probe dates | `pending` |
| Samsung split | pre/post-split raw OHLCV plus issuance fields, without inferred adjustment semantics | `pending` |
| Delisted stock | Hanjin Shipping price and issuance records joined by returned stable identifiers, with `lstgAbolDt=20170307` | `pending` |
| Dividends | returned record/payment dates and share class joined through returned identifiers | `pending` |
| Provider behavior | safe quota headers, exact row/byte totals, and any no-retry error | `pending` |
| Unobserved semantics | halts, corrections, code changes, and withdrawals remain `not_observed` unless directly present | `pending` |

## Required decisions

Assign Korean stock daily and Korean ETF daily separately as `feasible_for_E2`, `limited`, or
`failed`. A successful HTTP response is insufficient. Silent current-date substitution, incorrect
identity/date, duplicate pagination, a missing fixed delisted sample, absent explicit ETF identity,
schema/authentication/429 errors, or a failed raw verifier prevents an unconditional GO.

## Current stop record

No market-data request has been attempted. The only missing preflight condition is a user-supplied
decoded Public Data Portal key after utilization approval for the four admitted APIs.
