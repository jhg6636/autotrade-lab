# Gate E1 connectivity recovery — one-request packet

- Base commit: `9916b5f`
- Working branch: `agent/GATE-E1-CONNECTIVITY-RECOVERY`
- Preparation date: 2026-08-27 KST
- Plan SHA-256:
  `1740ba05109d918f4ccbcf72bca361749c8e1607dc91a0ca4db4476c347f5279`
- User approval: 2026-08-27 KST
- Stage: executed once; stopped for review with `schema_error`

## Why this is a new packet

The approved Gate E1-DATA run ended on its first slot with a redacted transport failure and zero
confirmed HTTP responses. Its zero-retry boundary forbids rerunning that command or reusing its
empty output directory. This packet is a new, minimal observation designed only to distinguish a
local/network connection problem from a provider HTTP, authentication, or response-schema result.
It does not resume the other 23 slots.

## Fixed boundary

Exactly one read-only request is allowed:

| Request | Endpoint | Parameters | Maximum |
| --- | --- | --- | --- |
| `connectivity_listing_2010_boundary` | Financial Services Commission KRX listed-instrument `getItemInfo` | `basDt=20100104`, `pageNo=1`, `numOfRows=1`, JSON | 1 request, 1 row, 65,536 raw bytes |

- retries: 0;
- fresh output: `research/probes/gate-e1-connectivity-recovery-20260827`;
- credential: decoded Public Data Portal key from the private mode-`0600` `.env.public-data` only;
- prohibited: the prior E1-DATA output directory or command, additional endpoints or dates,
  brokerage/account/order APIs, backtests, rankings, optimization, orders, and trades.

The result must be written as canonical `result.json` even when DNS, timeout, TLS, other transport,
HTTP, or schema failure occurs. Exception text, live URLs, and credential variants must never enter
the report. Only a structurally valid HTTP 200 JSON response may create one local raw body.

## Approval-bound command

Do not run until the user explicitly approves the exact plan hash above:

```bash
.venv/bin/python - <<'PY'
from pathlib import Path

from autotrade_lab.gate_e1_prep import (
    collect_gate_e1_connectivity_recovery,
    load_public_data_service_key,
    verify_gate_e1_connectivity_recovery,
)

output = Path("research/probes/gate-e1-connectivity-recovery-20260827")
key = load_public_data_service_key(Path(".env.public-data"))
try:
    collect_gate_e1_connectivity_recovery(
        output,
        decoded_service_key=key,
        approved_plan_sha256=(
            "1740ba05109d918f4ccbcf72bca361749c8e1607dc91a0ca4db4476c347f5279"
        ),
    )
finally:
    del key
verify_gate_e1_connectivity_recovery(output)
PY
```

Do not rerun the command after the single attempt. Stop for review regardless of outcome. A success
establishes only connectivity plus the returned one-row schema; it does not authorize the remaining
Gate E1-DATA slots or change the stock/ETF historical-data NO-GO by itself.

## Execution result

The approved command was executed once on 2026-08-27 KST from the fresh result branch and output
directory. The provider returned HTTP 200 with JSON content type and safe quota headers, so DNS,
TLS, and basic HTTP reachability were established. The body did not satisfy the pinned normal-data
schema and the packet recorded `schema_error` without retaining that body.

- attempts: 1 of 1;
- retries: 0;
- HTTP status: 200;
- declared response bytes: 142;
- safe quota observation: limit 10,000; remaining 9,999;
- outcome: `schema_error`;
- retained raw files, rows, and body bytes: 0/0/0;
- canonical result: `research/probes/gate-e1-connectivity-recovery-20260827/result.json`;
- credential, live URL, exception text, account access, order, or trade retained/performed: false.

This outcome proves connectivity only. It does not establish successful authentication, the exact
error/result code, the response envelope, historical coverage, or row semantics. The packet
deliberately discarded schema-failure bodies, so the exact mismatch cannot be reconstructed without
a new plan. No additional request is authorized by this result.

## Completion conditions

- exact plan hash matches the runtime packet before output creation;
- exactly one attempt and zero retries;
- canonical result verifies without a credential;
- no secret, live URL, exception text, or account/order data is retained;
- outcome is classified without overstating provider guarantees;
- coordinator reviews the result before proposing any further request.

All completion conditions were met for this one-attempt packet. The result is not a Gate E1-DATA
pass and does not reopen broad collection.

## Stop conditions

Stop before execution if the key file, permissions, plan hash, branch/base, or fresh output
preflight differs. During execution, any outcome ends the packet. Do not delete or replace a failed
result, change network surfaces to bypass a failure, or spend another request without a new plan and
approval.
