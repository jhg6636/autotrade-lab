# Gate E1 runtime-envelope parser update

- Base commit: `50cff2a`
- Working branch: `agent/GATE-E1-RUNTIME-ENVELOPE`
- Date: 2026-08-28 KST
- Stage: implementation and local verification
- Public-data requests: 0

## Evidence and decision

The separately approved schema diagnostic observed HTTP 200, provider code `00`, matching paging,
an empty item list, and a top-level `response` wrapper. The official Public Data Portal Swagger
shows JSON `header` and `body` at the top level, while the attached guide shows a `response` wrapper
for XML. The safe result does not retain the body, but its fixed categories establish the runtime
envelope without retaining provider-controlled text.

The shared response parser now admits exactly two normal-data envelope forms:

1. documented JSON: top-level `header` and `body`;
2. observed runtime JSON: a sole top-level `response` object containing `header` and `body`.

If documented fields and `response` coexist, or if the runtime wrapper has sibling top-level keys,
the parser fails closed. Both forms retain the same provider result-code, paging, total-count, item,
row-budget, secret, byte-budget, and raw-evidence checks. The request plan and its SHA-256 are not
changed.

## Scope boundary

This change performs no public-data request and does not authorize reuse of any completed plan or
output directory. It does not infer that every admitted Financial Services Commission endpoint will
return the same envelope. A future data run requires a new execution packet, fresh output, explicit
hash approval, and zero-retry stop rules.

No backtest, ranking, optimization, account access, order, or trade is in scope.

## Completion checks

- documented top-level success remains accepted;
- observed runtime wrapper succeeds in both collection and verification paths;
- ambiguous dual envelopes and malformed runtime wrappers fail closed;
- provider/paging/items/row/secret/raw-evidence guards remain active;
- the historical diagnostic artifact remains canonically verifiable;
- focused and full tests, Ruff check/format, and `git diff --check` pass;
- canonical strategy and source records remain unchanged.
