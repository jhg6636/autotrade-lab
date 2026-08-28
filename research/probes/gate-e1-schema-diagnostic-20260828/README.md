# Gate E1 schema-diagnostic result

This directory contains the safe canonical result of the separately approved one-request diagnostic
executed on 2026-08-28 KST. The request returned HTTP 200 JSON with provider result code `00`,
matching paging, an empty item list, and a runtime `response` wrapper that differs from the official
Swagger's top-level JSON schema.

- attempts: 1/1;
- retries: 0;
- outcome: `schema_error` / `documented_schema_mismatch`;
- response: 142 bytes, SHA-256
  `661ec92a32a8c54f05f3286335aee6a57076867696a4d1c0e7ad41df6ee989f4`;
- raw body retained: false;
- credential, provider message, live URL, account/order data retained: false;
- backtest, order, or trade performed: false.

`result.json` is the canonical fixed-category artifact. It does not authorize a retry, broad Gate
E1-DATA collection, or an undocumented parser change without review.
