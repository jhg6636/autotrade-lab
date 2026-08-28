# Active research handoff

Last updated: 2026-08-28 KST

## Active objective

Prepare, review, and seek exact-hash approval for one Gate E1 schema-diagnostic request. Official
Swagger and DOCX evidence confirms top-level `header`/`body` for JSON, so the parser remains strict.
The new diagnostic can distinguish a provider result code from a documented-schema mismatch without
retaining provider messages or failed raw bodies. Do not execute it before exact-hash approval, and
do not backtest, rank, optimize, access an account, order, or trade.

## Repository state

- Current main: Gate E1 connectivity-recovery result merge commit `d34057f`
- Working branch: `agent/GATE-E1-SCHEMA-PREP`, based on main `d34057f`
- Gate E1-DATA closeout PR: `#24`, merged as `9916b5f`; four intended documentation files and
  GitGuardian successful
- Gate E1 connectivity-recovery preparation PR: `#25`, merged as `6d94ee8`
- Gate E1 connectivity-recovery result PR: `#26`, merged as `d34057f`
- Gate E1 schema-diagnostic preparation PR: `#27`, open, mergeable, GitGuardian successful; no
  public-data request
- Gate C Phase 2 PR: `#19`, merged as `b83dfc7`
- Gate D PR: `#20`, merged as `d419aec`
- Gate D2 implementation/evidence commit: `0c91c23`
- Canonical strategies/index modified: false
- Gate D2 market-data requests: 12/12 succeeded; OAuth exchange: one
- Gate D2 credentials read locally: true; credential/token values retained in artifacts: false
- Backtest/ranking/trading performed: false
- Gate E1-DATA local slot attempts: 1/24; confirmed HTTP responses: 0; retries: 0
- Gate E1-DATA retained raw files/rows/bytes: 0/0/0; manifest created: false
- Gate E1 connectivity-recovery requests: 1/1; HTTP 200, `schema_error`, retries 0
- Gate E1 connectivity-recovery retained raw files/rows/body bytes: 0/0/0
- Gate E1 schema-diagnostic requests: 0/1; retries: 0; plan hash
  `f70bf4dc56edbbc280ccba08e9a1cfa571f5795c3fda48c44a04822d0545f167`

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

## Gate E0 source-resolution decision

- Direct KRX Open API is not the default durable archive: it is noncommercial-only, prohibits
  third-party provision, and prohibits using received information after contract termination.
- The Financial Services Commission Public Data Portal publications are the lowest-friction bounded
  feasibility candidates. Listed-instrument and stock-price metadata display no license restriction;
  issuance and dividend data are Public Nuri Type 2 (attribution, noncommercial only). Durable raw
  storage and backtest rights stay unknown until detailed conditions are fingerprinted in E1-PREP.
- Published time ranges are blank. Historical depth, delisted retention, correction semantics, and
  ETF lifecycle completeness remain untested.
- OpenDART supports identity and filing/correction evidence, with useful structured corporate-action
  fields from 2015 for some event types. It cannot define the point-in-time universe or complete
  adjusted-price factors.
- Korean stock daily: conditional GO to documentation-only E1-PREP; no data call yet.
- Korean ETF daily and Korean stock/ETF one-minute: remain NO-GO.
- `research/runs/GATE-E0.md` proposes E1-PREP followed by a separately approved maximum 24-request,
  1,200-row, 5 MiB E1-DATA plan.

## Gate E1-PREP status

- Official pages and public DOCX guides for all four admitted publications were retrieved into a
  temporary directory, fingerprinted, and not tracked or redistributed.
- Exact allowed operations: listed instruments, stock prices, investment-security prices, issuance
  V3 basic/history, and dividend V2.
- Issuance V3 prose/notice mentions `isinCd`, while its Swagger/request table omits it. The plan
  avoids the disputed parameter, always supplies `basDt`, and fails closed on runtime divergence.
- Rights decision for private noncommercial research: temporary evidence, durable private raw
  retention, internal noncommercial derivative/backtest use, and private derived-result retention
  are `documented`. Public Nuri Type 2 attribution applies to issuance/dividend; commercial and
  external use remain unauthorized.
- `src/autotrade_lab/gate_e1_prep.py` defines 24 immutable slots, maximum 1,200 rows and 5 MiB, exact
  allowlists, secret/redirect/stream/schema guards, no retries, and raw-evidence verification.
- Request-plan SHA-256:
  `ae802b8d4245a153af5abea3e2875049ee086e6556541ff3f8f1a5d2677198f0`.
- The later E1-DATA run loaded the private service key without printing or persisting it in tracked
  artifacts. All four admitted API applications were approved in the portal.
- Final adversarial review resolved approval-hash base-URL coverage, encoded-key header retention,
  and manifest/raw-set verification defects. No P1/P2 remains.

## Validation evidence

- Gate E0 final adversarial review: no P1/P2 findings
- Gate E0 official-source evidence SHA-256:
  `190949d88c00db72729781f5de3f9e928d3046dcc445fa88272928d073a99928`
- Gate E0 full repository tests: 117 passed; Ruff check/format and `git diff --check`: passed
- Gate E0 credential-pattern scan and canonical strategy/index isolation: passed
- Gate E0 API/key/data calls, backtests, rankings, account access, and trades: none
- Gate E0 PR `#22`: merged as `a92c09b`; correct `main` base, four intended files,
  GitGuardian success, clean/mergeable, and no review comments or submitted reviews
- Gate E1-PREP focused tests: 14 passed
- Gate E1-PREP full repository tests: 131 passed
- Gate E1-PREP Ruff check/format, `git diff --check`, credential-pattern scan, and canonical
  strategy/index isolation: passed
- Gate E1-PREP public data calls, key creation/read, backtests, rankings, account access, orders,
  and trades: none
- Gate E1-PREP PR `#23`: merged as `1dfc2c7`; correct `main` base, eight intended files,
  GitGuardian success
- `README.md` and `docs/ROADMAP.html` provide a derived milestone view; this handoff remains the
  operational source of truth.
- `research/runs/GATE-E1-DATA.md` pins the approved execution command, preflight, observation matrix,
  and no-retry stop rule. Its singular execution stopped on the first slot with a redacted transport
  failure; no response body or manifest was retained and no retry occurred.
- Gate E1-DATA closeout: 131 tests passed; Ruff check/format and `git diff --check` passed.
- Gate E1 connectivity-recovery preparation: 19 focused and 136 full tests passed; Ruff
  check/format and `git diff --check` passed; runtime plan hash pinned; no public-data request
  attempted.
- Gate E1 connectivity-recovery result: canonical verifier and credential-variant scan passed; 136
  full tests, Ruff check/format, and `git diff --check` passed after the single HTTP 200
  `schema_error`; no retry occurred.
- Gate E1 schema-diagnostic preparation: official portal Swagger and attached DOCX reviewed without
  a market-data request; JSON top-level `header`/`body` retained as the strict schema. Fixed-category
  provider/schema diagnostics, failed-body fingerprinting, secret-echo rejection, and canonical
  verification are implemented. Focused tests: 28 passed; full repository tests: 145 passed; Ruff
  check/format and `git diff --check`: passed. Public-data requests: 0.

- Full repository tests: 117 passed
- Ruff check and format check: passed
- `git diff --check`: passed
- Documentation-source fingerprints and Gate C raw-to-Parquet regeneration: passed
- Corrected Toss normalization reran byte-identically; existing crypto normalization still verifies
- Credential-pattern scan and canonical isolation: passed
- Gate D2 manifest-to-local-raw checksum/byte/count verification: passed
- PR `#20`: correct `main` base, 10 intended files, GitGuardian success, clean/mergeable, no review
  comments or submitted reviews before the final handoff update
- PR `#21`: merged as `bd8ceb0`; GitGuardian success, clean/mergeable, six intended files

## Next action

Review the Gate E1 schema-diagnostic preparation and present plan SHA-256
`f70bf4dc56edbbc280ccba08e9a1cfa571f5795c3fda48c44a04822d0545f167` for explicit user approval.
Do not execute the request as part of preparation, rerun either completed packet, or reuse an old
output directory.

## Resume instruction

Read `AGENTS.md`, this handoff, `research/runs/GATE-E1-SCHEMA-DIAGNOSTIC.md`,
`research/runs/GATE-E1-CONNECTIVITY-RECOVERY.md`,
`research/runs/GATE-E1-DATA.md`, `research/runs/GATE-D.md`, `research/runs/GATE-C.md`, and
`docs/INVESTOR_PROFILE.md`. Verify branch/base and execute only the singular next action above.
