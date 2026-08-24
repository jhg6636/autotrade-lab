# Active research handoff

Last updated: 2026-08-24 KST

## Active objective

Complete coordinator review of the user-approved bounded first-data capability probe under
`research/runs/GATE-C.md`. Both the public crypto and Toss market-data phases have been collected and
normalized. This is a data-capability result, not a strategy result.

## Repository state

- Working branch: `agent/GATE-C-toss-probe`
- Gate C Phase 2 base: `main` at `b790a2d`
- Gate B PR: `#16`, merged as `96f3e14`
- Gate C Phase 1 PR: `#18`, merged as `b790a2d`
- Canonical strategies/index modified: false
- Market data collected: 27 approved requests, 10,600 candle rows; 24 succeeded and 3 Toss
  stock-master requests returned `HTTP 429`
- Toss OAuth used: true; client credentials and bearer token persisted: false
- Account/order APIs used: false
- Backtest/ranking/trading performed: false

The last completed discovery aggregate remains 80 sources (26 usable, 53 incomplete, 1
inaccessible), 95 hypotheses (35 usable, 60 incomplete), and 2,282 suggestions. Its deterministic
SHA-256 is `f5f7213dc5a1abcb4b240eff748ed898b69145a16876327b9d82f2744e115fe9`.

## Gate B result

- All 35 canonical records have unknown timeframe/rule/data placeholders. All 35 usable LUNA-101
  hypotheses are context-only.
- One bounded pass inspected six Korean and six crypto public sources. It found no complete
  executable candidate for any of the eight target cells.
- All eight cells finish as `ambiguous_rule`; this is a feasibility state, not a rank.
- Current Toss documentation corrects the repository's former REST-only assumption: REST and
  WebSocket are available. Historical retention, point-in-time completeness, fill semantics, and
  redistribution rights remain unresolved.
- The proposed next sample is capped at 29 public/market-data requests, 10,600 candle rows, and
  25 MB. The user approved that bounded sample for Gate C on 2026-08-24. Toss access additionally
  requires credentials through an approved secret mechanism; account and order APIs remain
  forbidden.

## Active completion condition

- Phase 1 attempts exactly the 12 allowlisted public requests at most once each and remains within
  8,800 rows; combined Gate C remains within 29 requests, 10,600 rows, and 25 MB.
- Raw responses, request manifest, deterministic normalized Parquet, and quality report pass review.
- No credential or bearer-token persistence, private/account/order API, backtest, rank, canonical
  promotion, or trade occurs.
- Toss Phase 2 attempted exactly 15 allowlisted requests once each; no further request is permitted
  during coordinator review.

## Gate C Phase 1 result

- 12/12 allowlisted public requests succeeded without credentials or retries.
- 8,800 rows normalized; 0 duplicates, internal gaps, invalid OHLC rows, non-finite rows, negative
  volumes, or time-grid failures; 12 current in-progress candles were identified.
- Parquet regeneration was byte-identical at SHA-256
  `9a9d59f2dce69edce8d840309b079bb5b546dc665635b6d456ec0c6c4489fe10`.
- Raw bodies and Parquet remain local/Git-ignored pending provider redistribution review. Manifest,
  quality report, checksums, code, and tests are intended for the reviewed PR.

## Gate C Phase 2 result

- The user confirmed the mode-0600 local credential file and allowed IP before access.
- OAuth succeeded without persisting credentials or token. All 9 candle calls succeeded and
  produced 1,800 rows; active KOSPI master, four-security details, and market calendar succeeded.
- Three `/stocks/all` calls returned `HTTP 429` under the observed one-request/second limit. They were
  preserved without retry because only two request slots remained. The collector now applies a
  1.1-second interval between consecutive calls to that endpoint.
- Combined totals are 27/29 requests and 10,600/10,600 rows. Toss local artifact size is 666,288
  bytes; both phases remain below 25 MB.
- Toss structural quality passes with zero identity duplicates, invalid OHLC rows, non-finite rows,
  negative volumes, or grid failures under the documented Korean-market timing scope.
- Toss deterministic Parquet SHA-256 is
  `93e091692e181e80a55de02a7f0361dd33bf870262ba88184ddcfe2939966e38`.
- Timestamp event semantics, historical retention, point-in-time universe completeness, and
  redistribution rights remain unresolved. Raw bodies and Parquet remain local/Git-ignored.

## Validation evidence

- `.venv/bin/pytest -q`: 100 passed
- Ruff check and format check: passed
- `git diff --check`: passed
- Crypto and Toss raw-to-Parquet byte identity, manifest/raw checksum enforcement, allowlist
  integrity, row/request/storage budgets, structural OHLC/time-grid checks, and Toss credential/token
  redaction: passed
- Canonical unknown-field audit, 35 usable/context-only audit, eight-cell/eight-state audit,
  canonical isolation, and secret-pattern audit: passed
- PR `#16`: correct `main` base and branch head, four expected files, mergeable/clean, GitGuardian
  success, zero review comments, no submitted reviews, and verified merged state

## Broader-collection recommendation

Do not begin broad historical collection or backtesting yet. Gate C proves that the selected public
crypto and Toss candle surfaces are reachable and structurally normalizable within a bounded sample,
but it does not establish that the resulting history is point-in-time safe or legally redistributable.
The next gate should first resolve, from provider documentation or support, these four items:

1. whether Toss candle `timestamp` denotes interval open, close, or another event time;
2. maximum historical retention and pagination behavior for `1m` and `1d` candles;
3. whether historical listed/delisted membership can reconstruct a point-in-time Korean universe;
4. storage, derived-data, and redistribution permissions for raw and normalized records.

After those answers are recorded, authorize a new, separately budgeted sample with endpoint-aware
pacing. The current two unused request slots are not carried forward as permission. No strategy
backtest should start from this capability sample.

## Next action

Merge reviewed PR `#19`, then prepare the documentation-first Gate D described above. Do not spend
the two remaining request slots, backtest, rank, promote canonical records, or trade.

## Resume instruction

Read `AGENTS.md`, this handoff, `research/runs/GATE-C.md`, `research/runs/GATE-B.md`, and
`docs/INVESTOR_PROFILE.md`. Verify the branch and base before acting. Execute only the singular next
action above. Do not make another network request during review.
