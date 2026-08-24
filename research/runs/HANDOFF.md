# Active research handoff

Last updated: 2026-08-24 KST

## Active objective

Close LUNA-101 academic/replication discovery using the user-approved token-efficient gate: at least
30 usable hypotheses, complete usable-source linkage, and a local family/market/timeframe coverage
audit. Source count is descriptive rather than a quota.

Collection stays flat and source-neutral. Do not rank, optimize, backtest, implement strategies,
promote canonical records, call Toss, use credentials, or place orders during this goal.

## Completion condition

- LUNA-101 has at least 30 usable hypotheses/variants and every usable source reference resolves.
- A local coverage audit documents family, market, timeframe, direction, and scope concentrations.
- All batch findings are resolved and deterministic validation passes.
- The integration tracker and umbrella PR agree with the collection aggregate.
- Final Sol-level review approves readiness of the umbrella PR; canonical promotion remains a
  separate decision.

## Current repository state

- Working branch: `agent/LUNA-101-coverage-closeout`
- Starting integration commit: `ce392ba` (merge of reviewed LUNA-101-05 PR `#14`)
- Last coordinator-reviewed research content: LUNA-101-05 through `995e3ac`
- Required PR base: `integration/LUNA-101-academic-discovery`
- Previous batch PR: `#14`, merged as integration commit `ce392ba`
- Current batch PR: none; local coverage closeout is in progress
- Umbrella PR: `#8` targeting `main`
- Umbrella PR body: synchronized through merged LUNA-101-05 counts; completion gate update pending
- Worktree: coverage closeout documentation is under local review
- Canonical strategy/index modified: false
- Automatic relation merge: false
- Coordinator review passed after `493d55b`: the staging validator records context-only leverage
  while Korean executable applications remain long-only, nonnegative, and capped at exposure `1`.
  The normalized records, direction/polarity/exposure, source links, finite parameter sets, generated
  suggestions, append-only deltas, deterministic report, and canonical isolation passed review.

The checked-out `git rev-parse HEAD` is authoritative for the current documentation commit; do not
rewrite this handoff merely to embed its own commit hash.

Current aggregate:

- sources: 80 total, 26 usable, 53 incomplete, 1 inaccessible;
- hypotheses: 95 total, 35 usable, 60 incomplete, 0 inaccessible;
- suggestions: 2,282.

LUNA-101-06 was stopped before normalization review, commit, or PR after the user replaced the raw
source quota with the coverage closeout gate. Its planning branch is not part of integration. Partial
normalization is preserved only in local stash `aborted LUNA-101-06 partial normalization` and must
not be resumed without an explicit gap-driven request.

## Recent completed review

- TSMOM identity now recognizes only explicit, uniformly signed `X=…sgn(±r[t-lookback,t])`
  formulas. Positive lookback and weight variants retain `variant_of`; direct outer- and
  inner-negation counterexamples are `related_to`. Outer and inner signs are combined, so an
  explicitly double-negated return remains positive. Unsupported, non-return, or mixed formulas
  receive no inferred TSMOM identity.
- LUNA-101-02's documented delta is corrected to 6 source records and 9 hypothesis records. The
  five non-TSMOM candidates plus the learned CPD/DMN record are incomplete; the usable additions
  are the classical, `w=0.5`, and `w=1` TSMOM hypotheses alongside the two pre-batch usable
  hypotheses.
- The committed aggregate was regenerated twice and was byte-identical (SHA-256
  `a1f871213f33fa220e412d0ef20c81c30db381340f570708479814dffa73569c`): 20 sources (3 usable,
  17 incomplete), 22 hypotheses (5 usable, 17 incomplete), and 91 suggestions. All three intended
  TSMOM pairs are `variant_of`.
- Coordinator review found and this follow-up closes two bypasses: inner-negated returns and
  arbitrary non-return `sgn` arguments. Regression coverage also verifies negative numeric
  coefficients and explicit double negation.
- `.venv/bin/pytest -q` passed (`72 passed`); Ruff check and format check, `git diff --check`,
  and the canonical diff against `integration/LUNA-101-academic-discovery` are clean.
- Independent coordinator re-review passed at `63be5be`. It repeated all mandated checks and
  adversarially verified positive lookback/weight variants, outer and inner polarity reversal,
  negative coefficients, double negation, mixed signs, unsupported `sgn` arguments, and vague
  TSMOM text.

PR `#11` was mergeable/clean with no review threads and was merged into the integration branch.
The LUNA-101 completion target remains unmet.

## Most recent completed batch

LUNA-101-03 admitted exactly 20 audited public full-text inputs, adding 20 source records
(3 usable, 17 incomplete) and 23 source-linked hypotheses (6 usable, 17 incomplete). The trend
lane inspected 16 unique candidates, of which it opened 11 full texts (the ten admitted packets
and Valeyre); five other trend leads lacked retrievable rule-bearing full text. The reversion lane
inspected ten admitted candidates, so the lanes inspected 26 candidates total. Valeyre and the
five rejected trend leads are six overflow leads excluded from every record, count, and status
decision. Duplicate/repost and alternate URLs are excluded. No ranking, evidence score, backtest,
strategy code, canonical promotion, or automatic relation merge occurred.

The aggregate was regenerated twice and byte-identical at SHA-256
`c06d4bbb546d45c365ac8891b28106d296a332e645954581ac4311d91633e556`. It retains
`automatic_merge=false` and `canonical_records_modified=false`. The collection target remains
short by 74 usable sources and 19 usable hypotheses/variants; all local missing-rule and
conflicting-threshold cases remain incomplete.

Coordinator review inspected all 20 appended source records and 23 appended hypotheses against
the two evidence artifacts. It corrected the Moreira–Muir universe label from an ambiguous
`French market` phrase to the Ken French factor set and corrected the collection disclosure to
trend 16 inspected/11 full texts opened plus reversion 10 inspected. Direction, polarity,
timeframe, sizing, status, source references, explicit variants, and relation suggestions passed
re-review. Independent validation passed with 72 tests, clean Ruff/format/diff checks,
append-only deltas of 20 sources and 23 hypotheses, a byte-identical aggregate, and no canonical
diff.

## Most recent normalized batch

LUNA-101-04 normalized exactly 20 collector-inspected packets at validator-fix base `8a981bc`: 20
source records (14 usable, 5 incomplete, 1 inaccessible) and 22 hypotheses (15 usable, 7
incomplete). The AER Halloween record is inaccessible because its complimentary full-text PDF was
blocked by a Cloudflare challenge; no Sell-in-May rule was inferred. International seasonality and
the index-weight event study remain incomplete. Aggregate reruns were byte-identical at SHA-256
`50e02941abfe7ca2fc063a5490cde05a8a8333b5b5ce693d6fcfa1f5e4c38572`. A coordinator correction
at `960806a` added only schema/validator leverage safety support. Normalization semantic correction
`491997c` fixed merger exposure/sizing selection and finite-set status policy; Chinese J/K is
incomplete. Final semantic correction `493d55b` and independent coordinator reruns passed with 79
tests and clean Ruff/format/diff checks. PR `#13` passed remote checks and merged into integration as
`5a7d7e7`. No ranking, backtest, canonical promotion, Toss access, or orders occurred.

## Current batch scope

LUNA-101-05 starts from integration commit `5a7d7e7` and permits at most 20 new unique candidates
across two disjoint ten-candidate lanes. One lane covers public replication or version-pinned
research implementations; the other covers fixed-rule public academic artifacts. Selection may
favor deterministic rule-bearing evidence to improve usable yield, but the pool remains flat and
source-neutral. Collectors transcribe evidence and ambiguities only; final status and variant
decisions remain with the implementer and coordinator. The exact contract is in
`research/runs/LUNA-101-05.md`.

## Current normalization correction

The LUNA-101-05 normalization review found a truthful context-only exposure with no finite cap.
The staging hypothesis schema and validator now represent an absent lower or upper exposure bound as
JSON `null`: `minimum: null` means no finite lower bound and `maximum: null` means no finite upper
bound. Every executable application still requires two finite numeric bounds; Korean executable
applications remain long-only, nonnegative, and capped at `1`. Ordering is checked only when both
bounds are finite. Regression coverage includes context-only long-only `{0, null}` and long-short
`{null, null}` applications, executable-null rejection, finite reversed bounds, Korean leverage
rejection, and aggregate/comparator preservation of distinct unbounded exposure profiles. This is
staging-only support; canonical strategy schemas remain unchanged.

## Superseded normalized batch snapshot

The following initial LUNA-101-05 normalization counts were superseded by adversarial correction.
It had normalized the two verified evidence packets with SHA-256 values
`19429c7e1a10e7c21165b4d6c8d66332fbea701905d2b860d844d38edc6d5488` (replication) and
`0185dcfdb1111a5bc01d78f179c74f28aa8e7705548bb9e655ec81cc5e30b938` (fixed rule). It appends
exactly 20 unique source captures (8 usable, 12 incomplete) and 28 source-linked hypotheses
(15 usable, 13 incomplete). All learned policies, generic frameworks, missing-sizing rules,
unresolved parameters, and the performance-labelled BTC example remain incomplete. The pinned IMC
code was independently checked as winner-minus-loser; the Baltas TSMOM/risk-parity record preserves
source-specific provenance without claiming independent evidence weight. The aggregate reran
byte-identically at SHA-256 `7c3f55280487aff496e093f582a2837abe9b4cbc5005d7221e2207fc5e417ddd` with
`automatic_merge=false` and `canonical_records_modified=false`. Coordinator review remains required.

## Corrected normalization state

LUNA-101-05 adversarial correction retains exactly 20 appended sources (6 usable, 14 incomplete)
and 28 appended hypotheses (9 usable, 19 incomplete). It marks Sepp European, JSE breakout, all BLL
signal-return study records, and Ferretti HRP incomplete; IVP remains usable. Sepp American is bounded
at `[-10,10]` by its literal direct-runner default. Sepp normalized-sign TSMOM and Baltas are usable
only with context-only `{minimum: null, maximum: null}`, explicitly meaning source-stated uncapped
symmetric volatility scaling rather than unknown sizing. Corrected aggregate reruns were byte-identical
at SHA-256 `f5f7213dc5a1abcb4b240eff748ed898b69145a16876327b9d82f2744e115fe9` with
`automatic_merge=false` and `canonical_records_modified=false`.

Independent coordinator review passed at `995e3ac`. It rechecked all 20 appended source records and
28 appended hypotheses, null-bound context semantics, direction/polarity/exposure, exact append-only
deltas, unique source and hypothesis IDs, unique source URLs, source references, deterministic report
bytes, and canonical isolation. The complete repository suite passed with 84 tests plus clean Ruff,
format, and diff checks.

## Next action

Validate the local coverage audit and updated completion contract, then open a small closeout PR to
`integration/LUNA-101-academic-discovery`. Do not resume generic source collection.

## Resume instruction

```text
Read AGENTS.md, docs/AGENT_WORKFLOW.md, research/runs/HANDOFF.md, and the linked research workflow.
Recreate the token-efficient LUNA-101 closeout goal. Keep the coordinator in the foreground and do
not delegate or resume web collection unless the user explicitly names a coverage gap. Verify the
recorded Git state, then execute only the handoff's Next action and preserve all stop conditions.
```
