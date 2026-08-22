# Active research handoff

Last updated: 2026-08-21 KST

## Active objective

Complete LUNA-101 academic/replication discovery through bounded reviewed batches until the lane
contains at least 80 usable sources and 30 usable distinct hypotheses or explicit variants, or a
documented system-wide blocker prevents further progress.

Collection stays flat and source-neutral. Do not rank, optimize, backtest, implement strategies,
promote canonical records, call Toss, use credentials, or place orders during this goal.

## Completion condition

- LUNA-101 reaches 80 usable sources and 30 usable hypotheses/variants.
- All batch findings are resolved and deterministic validation passes.
- The integration tracker and umbrella PR agree with the collection aggregate.
- Final Sol-level review approves readiness of the umbrella PR; canonical promotion remains a
  separate decision.

## Current repository state

- Working branch: `agent/LUNA-101-03-academic-batch`
- Starting integration commit: `d2484fd` (merge of reviewed LUNA-101-02 PR `#11`)
- Last coordinator-reviewed research content: LUNA-101-03 through `e0fe32b`
- Required PR base: `integration/LUNA-101-academic-discovery`
- Remote LUNA-101-03 batch branch/PR: pushed; Draft PR `#12`
- Previous batch PR: `#11`, merged as integration commit `d2484fd`
- Umbrella PR: `#8` targeting `main`
- Umbrella PR body: synchronized through LUNA-101-02
- Worktree: LUNA-101-03 normalized evidence batch approved locally and published to Draft PR `#12`
- Canonical strategy/index modified: false
- Automatic relation merge: false

The checked-out `git rev-parse HEAD` is authoritative for the current documentation commit; do not
rewrite this handoff merely to embed its own commit hash.

Current aggregate:

- sources: 40 total, 6 usable, 34 incomplete, 0 inaccessible;
- hypotheses: 45 total, 11 usable, 34 incomplete, 0 inaccessible;
- suggestions: 459.

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

## Current batch scope

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

## Next action

Verify PR `#12` checks, review threads, exact base/head, and mergeability before marking it ready.

## Resume instruction

```text
Read AGENTS.md, docs/AGENT_WORKFLOW.md, research/runs/HANDOFF.md, and the linked research workflow.
Recreate the active LUNA-101 goal. Keep the coordinator in the foreground, delegate bounded
implementation to Terra and mechanical collection to Luna, and do not ask the user to switch
models. Verify the recorded Git state, then execute only the handoff's Next action and preserve all
stop conditions.
```
