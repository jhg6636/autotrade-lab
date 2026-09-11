# Gate E1 Korean daily-data eligibility — execution packet

- Base commit: `ff7ca321adbb86258aa326ceacf94196edc114bc`
- Working branch: `agent/GATE-E1-DATA-V2-PREP`
- Prepared: 2026-08-28 KST
- Final review: 2026-09-04 KST
- Packet ID: `gate-e1-eligibility-20260828-v1`
- Packet SHA-256: `605df1d560b33116823f91033df324876a671cdec51ceb794630009452dd25b6`
- Output: `research/probes/gate-e1-eligibility-20260828-v1`
- Public-data calls during preparation: 0

## Purpose and authorization

The active `KR-E1-ELIGIBILITY-CLOSEOUT` goal authorizes one fresh, bounded, read-only execution after
this preparation is reviewed and merged. The packet determines whether the official sources are
eligible for a later limited E2 dataset design. It does not authorize a broad historical download,
backtest, ranking, optimization, account access, order, short sale, paper trade, or live trade.

## Immutable execution envelope

- exactly 24 ordered HTTPS GET slots; no replacement and no reuse of unused budget;
- maximum 1,200 returned rows, 5 MiB total bytes read, and 218,000 retained raw bytes per slot;
  a streaming response without `Content-Length` may consume one additional non-retained byte solely
  to prove overflow, records that byte in `response_bytes_read`, and stops the packet;
- concurrency 1, timeout 30 seconds, redirects disabled, retries 0;
- exact fresh output directory above; any existing file, directory, or symlink stops before key read;
- decoded key loaded only from mode-0600 `.env.public-data`; neither key nor encoded variants may
  enter selected headers, bodies retained as raw evidence, or the manifest;
- the first transport, HTTP, content-type, provider, envelope, paging, JSON, row/byte, secret, or
  semantic failure stops all later requests and writes a fixed-category terminal manifest;
- successful empty responses are observations and continue; no sample may be substituted.

The request table remains the 24-slot table pinned by `gate_e1_request_plan()` with request-plan
SHA-256 `ae802b8d4245a153af5abea3e2875049ee086e6556541ff3f8f1a5d2677198f0`.
The response-field contract is separately pinned in `research/runs/GATE-E1-FIELD-CONTRACT.md`.

## Deterministic eligibility decision

The terminal manifest evaluates three deliberately different scopes:

- Korean stock daily can be `feasible_for_e2` only if the complete packet demonstrates current
  listing/price joins, 2010 boundary evidence, both two-page checks, a KOSDAQ sentinel, Samsung split
  and dividend identity joins, and the Hanjin delisted identity join. Missing evidence is `limited`
  or `failed`, never inferred.
- broad Korean ETF daily is at most `limited`, because this packet contains no delisted-ETF or full
  point-in-time-universe sample.
- KODEX 200 as a single instrument can be `feasible_for_e2` only when listing and both price dates
  share the exact ISIN and a consistent short-code/name alias.

Even a completely successful packet records `backtest_decision: no_go`. E1 can authorize only the
design of a later E2 collection/quality gate; it cannot establish a backtest-grade dataset by itself.

## Singular post-merge command

Run from a fresh branch based on the merge commit, only after verifying the packet hash and output
absence:

```bash
.venv/bin/python - <<'PY'
from pathlib import Path

from autotrade_lab.gate_e1_eligibility import (
    OUTPUT_DIR,
    collect_gate_e1_eligibility_from_key_file,
    verify_gate_e1_eligibility,
)

manifest = collect_gate_e1_eligibility_from_key_file(
    OUTPUT_DIR,
    key_file=Path(".env.public-data"),
    approved_packet_sha256="605df1d560b33116823f91033df324876a671cdec51ceb794630009452dd25b6",
)
verify_gate_e1_eligibility(OUTPUT_DIR)
print(manifest["terminal_state"])
PY
```

Do not rerun after any request is attempted. A stopped terminal manifest is the result of this
packet. Any credential/security anomaly, paid/licensing decision, cap expansion, unsafe provider or
schema change, or completed GO/NO-GO requiring an E2 choice returns control to the user.
