# Active research handoff

Last updated: 2026-08-24 KST

## Active objective

Record and review the user-authorized Gate D2 bounded Toss market-data observation. Preserve the
boundary between documented, observed, and unknown facts and decide whether Gate E changes. Do not
call account/order APIs, backtest, rank, optimize, promote canonical records, or trade.

## Repository state

- Working branch: `agent/GATE-D2-observed-probe`
- Base: merged Gate D on `origin/main` at `d419aec`
- Gate C Phase 2 PR: `#19`, merged as `b83dfc7`
- Gate D PR: `#20`, merged as `d419aec`
- Canonical strategies/index modified: false
- Gate D2 market-data requests: 12/12 succeeded; OAuth exchange: one
- Gate D2 credentials read locally: true; credential/token values retained in artifacts: false
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

## Gate D2 observed result

- Exactly 12 market-data calls, 800 candle rows, 649,329 raw bytes, no retries.
- `1m` and `1d` two-page cursor observations were descending with zero cross-page duplicates.
- Targeted `005930` daily access returned 200 rows back to 2017-07-14.
- At the 2018 split breakpoint, pre-split adjusted prices/volumes changed by exact factors 1/50 and
  50; post-split adjusted and unadjusted values matched.
- Historical KR calendar lookup for 2018-05-04 succeeded.
- Current active masters returned KOSPI 2,476 and KOSDAQ 1,825 records. Both `DELISTED` calls returned
  empty arrays, so the API did not provide a historical-universe sample.
- Manifest SHA-256:
  `ab5d48f3ce930238cc3c96e671b5963a15823efdd98484d40afcf830442fde52`.

## Gate E decision

**NO-GO** for broad historical collection and strategy backtesting. Reachability and structural
normalization do not establish point-in-time validity or data-use permission. The investor's desired
high return does not weaken survival, bias, corporate-action, or licensing gates.

## Validation evidence

- Full repository tests: 117 passed
- Ruff check and format check: passed
- `git diff --check`: passed
- Documentation-source fingerprints and Gate C raw-to-Parquet regeneration: passed
- Corrected Toss normalization reran byte-identically; existing crypto normalization still verifies
- Credential-pattern scan and canonical isolation: passed
- Gate D2 manifest-to-local-raw checksum/byte/count verification: passed
- PR `#20`: correct `main` base, 10 intended files, GitGuardian success, clean/mergeable, no review
  comments or submitted reviews before the final handoff update

## Next action

Review the Gate D2 diff and evidence, run the full repository checks, and merge only if the tracked
manifest contains no credentials and the five documented-contract blockers remain fail-closed.

## Resume instruction

Read `AGENTS.md`, this handoff, `research/runs/GATE-D.md`, `research/runs/GATE-C.md`, and
`docs/INVESTOR_PROFILE.md`. Verify branch/base and execute only the singular next action above.
