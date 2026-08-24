# Active research handoff

Last updated: 2026-08-24 KST

## Active objective

Complete the documentation-first Gate D under `research/runs/GATE-D.md`. Convert only documented
provider facts into fail-closed market-data contracts, preserve observed and unknown states, and
decide whether broad collection or Gate E backtesting is safe. Do not call market/account/order APIs,
backtest, rank, optimize, promote canonical records, or trade.

## Repository state

- Working branch: `agent/GATE-D-data-contract`
- Base: merged Gate C on `main` at `b83dfc7`
- Gate C Phase 2 PR: `#19`, merged as `b83dfc7`
- Canonical strategies/index modified: false
- Gate D market-data/OAuth/account/order requests: zero
- Gate D credentials read: false
- Backtest/ranking/trading performed: false

The last completed discovery aggregate remains 80 sources (26 usable, 53 incomplete, 1
inaccessible), 95 hypotheses (35 usable, 60 incomplete), and 2,282 suggestions. Its deterministic
SHA-256 is `f5f7213dc5a1abcb4b240eff748ed898b69145a16876327b9d82f2744e115fe9`.

## Gate C result retained

- Public crypto: 12/12 requests succeeded and 8,800 candles normalized.
- Toss: 15 requests attempted, all 9 candle requests plus 3 reference requests succeeded, and 3
  stock-master requests returned `HTTP 429` without retry.
- Combined Gate C: 27/29 requests and 10,600/10,600 candle rows; no account/order API or trade.
- Raw bodies and Parquet remain local/Git-ignored because redistribution rights are unresolved.
- Gate D corrected Toss daily completion: canonical documentation confirms timestamp-as-start, but
  daily candle session scope is unknown. The 1,000 daily rows now have null close/completion; 8 of
  800 one-minute rows were incomplete at retrieval.
- Corrected Toss deterministic Parquet SHA-256:
  `1069360f6694126fae5246c09969b30932c00d62b6d5b4c6914c095da475da25`.

## Gate D official-source result

Official sources were retrieved on 2026-08-24 without authentication or API calls. The canonical
OpenAPI version is `1.2.14`, SHA-256
`a7b32ba754401d13fa649ba91eebd212420eb1afab28e9c2c0d6ea8d43055fed`; official `llms.txt` SHA-256 is
`a57be4baa04d60b68897b2766802bd626b9c88d7fcea1c5306d2318cb36a9988`.

Documented:

- candle `timestamp` is the offset-aware interval start;
- intervals are `1m`/`1d`, maximum page size is 200, `before` is inclusive, `nextBefore` is the
  response cursor, and null terminates;
- `adjusted` defaults true and toggles applied/unapplied adjusted prices;
- stock snapshots support `SCHEDULED`/`ACTIVE`/`DELISTED`, with detail `listDate`/`delistDate`;
- KR calendar uses KST and integrated KRX+NXT sessions for previous/current/next business days;
- chart and stock-all groups are listed at 20 TPS and 1 TPS respectively, with runtime headers
  authoritative.

Unknown:

- guaranteed `1m`/`1d` retention;
- point-in-time complete historical universe and delisted-history coverage;
- corporate-action scope, factors, effective time, and revision policy;
- daily candle session aggregation and completion boundary;
- local storage, derived use, display, and redistribution rights.

## Contract implementation

- `src/autotrade_lab/market_data_contract.py` represents documented/observed/unknown provenance,
  timestamp meaning, pagination, adjustment, universe validity, sessions, runtime pacing, and data
  rights as immutable contracts.
- Validators reject naive timestamps, unknown interval meaning, missing/mismatched daily session
  ends, non-descending pages, repeated/non-monotone cursors, ambiguous delist boundaries, invalid TPS,
  and empty nonterminal pages.
- `gate_e_blockers()` returns five stable blockers for the unresolved categories above.
- The Toss normalizer uses documented one-minute bounds and preserves daily close/completion as null.

## Gate E decision

**NO-GO** for broad historical collection and strategy backtesting. Reachability and structural
normalization do not establish point-in-time validity or data-use permission. The investor's desired
high return does not weaken survival, bias, corporate-action, or licensing gates.

## Conditional Gate D2 plan

`research/runs/GATE-D.md` contains an unapproved maximum 12-request, 800-row, 5 MB follow-up sample.
It may be proposed only after official support clarifies data rights and narrows the other unknowns.
Unused Gate C requests are not carried forward. Exact symbols/event/date/requests and secret handling
require separate user approval.

## Validation evidence

- Full repository tests: 114 passed
- Ruff check and format check: passed
- `git diff --check`: passed
- Documentation-source fingerprints and Gate C raw-to-Parquet regeneration: passed
- Corrected Toss normalization reran byte-identically; existing crypto normalization still verifies
- Credential-pattern scan and canonical isolation: passed

## Next action

Commit the reviewed Gate D package and open a PR against `main`. Do not execute Gate D2 or contact
support on the user's behalf.

## Resume instruction

Read `AGENTS.md`, this handoff, `research/runs/GATE-D.md`, `research/runs/GATE-C.md`, and
`docs/INVESTOR_PROFILE.md`. Verify branch/base and execute only the singular next action above.
