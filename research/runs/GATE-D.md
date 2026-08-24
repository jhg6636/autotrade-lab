# Gate D — documentation-first market-data contract

- Base commit: `b83dfc7cd1a9f01ad4705dea291b5211ad309abe`
- Working branch: `agent/GATE-D-data-contract`
- Retrieval date: 2026-08-24 KST
- Stage: official-source review and fail-closed contract implementation

## Objective and boundaries

Gate D decides which provider facts are strong enough to become executable data contracts. It does
not measure strategy performance. Official provider documentation is authoritative for documented
behavior; Gate C artifacts may establish only observed behavior. Missing documentation remains
unknown and must not be filled from examples or inference.

No credentials, market-data API calls, account/order APIs, acceptance of terms, backtest, ranking,
optimization, canonical promotion, or trade are authorized in this gate. Documentation fetches do
not spend a market-data request budget.

## Official sources

| Source | Role | Retrieval fingerprint |
| --- | --- | --- |
| [Canonical OpenAPI 3.1 JSON](https://openapi.tossinvest.com/openapi-docs/latest/openapi.json) | REST endpoint, parameter, response schema, and rate-group source of truth; version `1.2.14` | SHA-256 `a7b32ba754401d13fa649ba91eebd212420eb1afab28e9c2c0d6ea8d43055fed` |
| [LLM integration index](https://developers.tossinvest.com/llms.txt) | Official source-of-truth routing and REST/WebSocket capability index | SHA-256 `a57be4baa04d60b68897b2766802bd626b9c88d7fcea1c5306d2318cb36a9988` |
| [Developer guide](https://developers.tossinvest.com/docs) | Rate-limit table, response headers, and retry guidance | Dynamic page; version shown as `1.2.14` |
| [Open API product page](https://corp.tossinvest.com/ko/open-api) | Product-level capability and investor notice | Dynamic page |
| [Toss Securities terms index](https://corp.tossinvest.com/ko/terms) | Search for an applicable public Open API data license | No Open API market-data storage/redistribution grant located |

The interactive developer pages are JavaScript-rendered. The official `llms.txt` explicitly routes
agents to the server-owned OpenAPI JSON, so the JSON—not search snippets—is used for field semantics.

## Evidence matrix

| Contract area | Status | What is established | What remains unknown |
| --- | --- | --- | --- |
| Candle timestamp | documented | `Candle.timestamp` is an offset-aware ISO 8601 date-time and is explicitly the candle start time. | Whether a daily candle represents KRX-only, NXT-only, or an integrated session, and which session end makes it final. |
| Interval and pagination | documented + observed | Intervals are `1m` and `1d`; `count` is 1–200; `before` is inclusive; the response `nextBefore` is passed unchanged and `null` terminates. Gate C observed each nonterminal cursor strictly before the oldest returned candle. | Guaranteed retention/lookback for either interval; whether future server versions may produce an overlapping inclusive boundary. Consumers must deduplicate by candle identity and reject stalled cursors. |
| Adjustment | documented toggle | `adjusted` is Boolean, defaults to `true`, and selects applied versus unapplied adjusted prices. | Covered corporate actions, adjustment factors, factor effective time, dividend treatment, revision policy, and an adjustment-event feed. |
| Universe | documented snapshot, incomplete history | `/stocks/all` supports `SCHEDULED`, `ACTIVE`, and `DELISTED`; `/stocks` exposes KST `listDate` and `delistDate`; stock-all is unpaginated, symbol-sorted, and documented as daily-batch/locally cacheable. | Completeness and retention of delisted records, historical as-of snapshots, symbol/ISIN reuse behavior, and candle availability after delisting. The description also limits results to Toss-tradable securities, so it cannot prove a complete exchange universe. |
| Calendar and timezone | partially documented | KR calendar times are KST (`+09:00`), integrated KRX+NXT, and return previous/current/next business-day sessions; holidays have `integrated=null`. | Historical calendar retention, ad-hoc closure revisions, special close days beyond the returned window, and exact candle-to-session attribution. |
| Rate limits | documented, runtime-authoritative | `MARKET_DATA_CHART` is listed at up to 20 TPS and `STOCK_ALL` at up to 1 TPS. Limits may change without notice; `X-RateLimit-*` and `Retry-After` are authoritative. | Daily/monthly quotas, per-IP overlays, and provider burst implementation beyond the returned headers. |
| Storage and redistribution | unknown | The product page permits access to market data after authentication. The OpenAPI document declares no `termsOfService` or data license. | Local retention duration, backtest/ML-derived use, public display, redistribution, commercial use, attribution, and underlying exchange/vendor restrictions. Access is not permission. |

## Corrections to prior assumptions

- The prior Gate C normalizer's choice to interpret Toss `timestamp` as interval open is now backed
  by the canonical schema rather than inference.
- A daily bar cannot be declared complete merely by adding 24 hours to KST midnight. The documented
  calendar contains pre-, regular-, and after-market sessions, while the candle-to-session scope is
  not stated. Daily completion therefore remains fail-closed.
- `status=DELISTED` and `listDate`/`delistDate` support individual validity metadata, but they do not
  establish a point-in-time complete universe.
- Official `llms.txt` and the canonical OpenAPI description include WebSocket support. A stale
  JavaScript page/search rendering that says REST-only is not used as source of truth.

## Required provider-neutral contract

The implementation must make documented, observed, and unknown states explicit. It must reject
naive timestamps, model start-labelled candles without silently deciding daily session completion,
validate descending pages and monotone cursors, distinguish individual listing validity from
universe completeness, pace from current response-header limits, and expose stable blockers before
Gate E. Unknown retention, historical-universe completeness, corporate-action methodology, daily
completion scope, or redistribution permission is sufficient to prevent a point-in-time backtest.

## Support questions

1. What guaranteed lookback or retention applies separately to `1m` and `1d` candles?
2. Which KR sessions and venues are aggregated into each interval, and when is a daily candle final?
3. Is `status=DELISTED` complete over a stated historical period, and is there a supported historical
   as-of universe or symbol-lifecycle feed?
4. Which corporate actions are covered by `adjusted=true`, how are factors calculated/effective, and
   can historical adjusted candles be revised?
5. May an individual Open API client retain raw market data locally, generate backtest/model-derived
   data, display results, or redistribute raw/derived records? What retention, attribution,
   commercial-use, and exchange/vendor restrictions apply?
6. Are there quotas or throttles beyond the documented client × API-group TPS and runtime headers?

The user must send these questions through an official support channel. This repository must record
the answer and its effective date before treating it as a contract fact.

## Conditional minimal follow-up probe — not authorized

Only after the storage terms permit local evidence and support answers narrow the unknowns, propose
a new Gate D2 budget for user review: at most 12 market-data requests, 800 candle rows, and 5 MB.

- four candle calls: two-page `1m` and `1d` pagination boundary checks on one security;
- two daily candle calls: adjusted/unadjusted comparison around one externally documented corporate
  action selected before collection;
- four paced universe calls: KOSPI/KOSDAQ × ACTIVE/DELISTED;
- one batched stock-detail call for selected active/delisted symbols;
- one KR calendar call for the preselected event date.

Each request is attempted once. `/stocks/all` calls are separated according to the latest response
header with safety margin. No previous unused budget is carried forward. D2 remains prohibited until
the user separately approves its exact symbols, event, date, request table, and secret mechanism.

## Gate E decision

Current decision: **NO-GO** for broad collection and strategy backtesting. Reachability, start-time
semantics, basic pagination, and structural normalization are established, but the five blockers in
the required contract are not. The small-capital/high-upside persona does not justify weakening
point-in-time, corporate-action, or licensing controls.
