# Gate E1 schema diagnostic — approval packet

- Base commit: `d34057f`
- Working branch: `agent/GATE-E1-SCHEMA-PREP`
- Preparation date: 2026-08-28 KST
- Plan SHA-256:
  `f70bf4dc56edbbc280ccba08e9a1cfa571f5795c3fda48c44a04822d0545f167`
- User approval: granted 2026-08-28 KST
- Stage: executed once; stopped for review with documented/runtime JSON divergence

## Why another packet is necessary

The completed connectivity packet reached the provider once with HTTP 200 and JSON content type,
then classified the 142-byte body as `schema_error`. Its safety rule discarded unsuccessful bodies,
so the exact cause cannot be recovered from the retained artifact. That packet cannot be rerun.

On 2026-08-28, the official Public Data Portal page and its attached DOCX guide were reviewed
without calling the market-data endpoint. The embedded Swagger specifies JSON with top-level
`header` and `body`; the DOCX response example wraps those fields in `response` only for XML. The
implementation therefore keeps the documented top-level JSON schema strict instead of accepting a
speculative JSON wrapper. Temporary documentation fingerprints, not tracked or redistributed:

- portal HTML: 208,481 bytes, SHA-256
  `a8dddb7c6d9d7a3509eb14a306e806ba7323d07608a8cd14c05f404234ae30e1`;
- official DOCX: 342,113 bytes, SHA-256
  `f5c34871d834daea234cfdb4d8975ff934d057cd79a3496ab47219f01869bb09`.

Official source: <https://www.data.go.kr/data/15094775/openapi.do>

## Fixed boundary

Exactly one new read-only request is proposed:

| Request | Endpoint | Parameters | Maximum |
| --- | --- | --- | --- |
| `schema_listing_2010_boundary` | Financial Services Commission KRX listed-instrument `getItemInfo` | `basDt=20100104`, `pageNo=1`, `numOfRows=1`, JSON | 1 request, 1 row, 65,536 raw bytes |

- retries: 0;
- fresh output: `research/probes/gate-e1-schema-diagnostic-20260828`;
- credential: decoded Public Data Portal key from private mode-`0600` `.env.public-data` only;
- prohibited: prior output directories, additional dates/endpoints, brokerage/account/order APIs,
  backtests, rankings, optimization, orders, and trades.

The diagnostic records fixed categories only: transport or HTTP failure, invalid content type or
JSON, documented-schema mismatch, or a two-digit provider result code. It may also record fixed
envelope, paging, and item-shape categories. Provider-controlled messages, exception text, live
URLs, and credential variants are never retained. A failed JSON body is represented only by its
byte count and SHA-256 after a credential scan; only a valid documented normal response may create
one local raw file.

## Approval-bound command

Do not run until the user explicitly approves the exact plan hash above:

```bash
.venv/bin/python - <<'PY'
from pathlib import Path

from autotrade_lab.gate_e1_prep import (
    collect_gate_e1_schema_diagnostic,
    load_public_data_service_key,
    verify_gate_e1_schema_diagnostic,
)

output = Path("research/probes/gate-e1-schema-diagnostic-20260828")
key = load_public_data_service_key(Path(".env.public-data"))
try:
    collect_gate_e1_schema_diagnostic(
        output,
        decoded_service_key=key,
        approved_plan_sha256=(
            "f70bf4dc56edbbc280ccba08e9a1cfa571f5795c3fda48c44a04822d0545f167"
        ),
    )
finally:
    del key
verify_gate_e1_schema_diagnostic(output)
PY
```

Do not rerun after the single attempt. Stop for review regardless of outcome. Even a successful row
establishes only the listed-instrument endpoint's one-request schema; it does not authorize the
remaining Gate E1-DATA slots or reopen broad historical collection.

## Execution result

The approved command was executed exactly once on 2026-08-28 KST from merged `main` commit
`4657094`. It returned HTTP 200 and JSON with provider result code `00`. Paging matched the approved
request and `items.item` was an empty list, but the runtime JSON placed the documented `header` and
`body` inside a top-level `response` object. The strict documented parser therefore correctly
stopped with `schema_error` and retained no raw body.

- attempts: 1/1;
- retries: 0;
- HTTP status: 200;
- provider result code: `00`;
- diagnostic: `documented_schema_mismatch`;
- runtime envelope/items/paging: `response_wrapped` / `item_list` / `matches`;
- observed rows: 0;
- response bytes: 142;
- response SHA-256:
  `661ec92a32a8c54f05f3286335aee6a57076867696a4d1c0e7ad41df6ee989f4`;
- safe quota observation: limit 10,000; remaining 9,999;
- raw files: 0;
- canonical result: `research/probes/gate-e1-schema-diagnostic-20260828/result.json`;
- provider message, credential, live URL, account/order data, backtest, order, or trade retained or
  performed: false.

This is direct evidence of a documentation/runtime envelope divergence for this request, not an
authentication failure. It is not yet evidence that every admitted Financial Services Commission
endpoint uses the same wrapper. The packet is complete and must not be rerun.

## Completion conditions

- exact runtime hash matches before output creation;
- exactly one attempt, one-row cap, 64 KiB cap, and zero retries;
- canonical result verifies without a credential;
- no provider message, secret, live URL, exception text, account/order data, or failed raw body is
  retained;
- result distinguishes provider status from structural failure using only fixed categories;
- coordinator reviews the result before proposing any additional request.

## Stop conditions

Stop before execution if the key file, permission mode, exact hash, branch/base, or fresh output
preflight differs. Any result ends the packet. Do not delete or replace a failed result, loosen the
official schema based on inference, bypass a network or provider failure, or spend another request
without a new plan and approval.
