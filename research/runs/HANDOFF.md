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

- Working branch: `agent/LUNA-101-02-academic-batch`
- Last coordinator-reviewed research commit: `66a3708` (`LUNA-101-02: fix TSMOM variants and counts`)
- Required PR base: `integration/LUNA-101-academic-discovery`
- Remote batch branch: `origin/agent/LUNA-101-02-academic-batch`; the polarity/count rework is
  intentionally unpushed pending independent coordinator review
- Draft batch PR: `#11`, targeting `integration/LUNA-101-academic-discovery`
- Umbrella PR: `#8` targeting `main`
- Executor worktree: clean after the implementation commit; coordinator review pending
- Canonical strategy/index modified: false
- Automatic relation merge: false

The checked-out `git rev-parse HEAD` is authoritative for the current documentation commit; do not
rewrite this handoff merely to embed its own commit hash.

Current aggregate:

- sources: 20 total, 3 usable, 17 incomplete, 0 inaccessible;
- hypotheses: 22 total, 5 usable, 17 incomplete, 0 inaccessible;
- suggestions: 91.

## Resolved findings and executor verification

- TSMOM identity now recognizes only explicit, uniformly signed `X=…sgn(…)` formulas. Positive
  lookback and weight variants retain `variant_of`; the direct `X=-sgn(r[t-252,t])` counterexample
  is covered as `related_to`. Unsupported or mixed formulas receive no inferred TSMOM identity.
- LUNA-101-02's documented delta is corrected to 6 source records and 9 hypothesis records. The
  five non-TSMOM candidates plus the learned CPD/DMN record are incomplete; the usable additions
  are the classical, `w=0.5`, and `w=1` TSMOM hypotheses alongside the two pre-batch usable
  hypotheses.
- The committed aggregate was regenerated twice and was byte-identical (SHA-256
  `a1f871213f33fa220e412d0ef20c81c30db381340f570708479814dffa73569c`): 20 sources (3 usable,
  17 incomplete), 22 hypotheses (5 usable, 17 incomplete), and 91 suggestions. All three intended
  TSMOM pairs are `variant_of`.
- `.venv/bin/pytest -q` passed (`69 passed`); Ruff check and format check, `git diff --check`,
  and the canonical diff against `integration/LUNA-101-academic-discovery` are clean.
- The batch remains not merge-ready pending independent coordinator review.

## Next action

Independently review the LUNA-101-02 polarity/count rework before any push or merge.

## Resume instruction

```text
Read AGENTS.md, docs/AGENT_WORKFLOW.md, research/runs/HANDOFF.md, and the linked research workflow.
Recreate the active LUNA-101 goal. Keep the coordinator in the foreground, delegate bounded
implementation to Terra and mechanical collection to Luna, and do not ask the user to switch
models. Verify the recorded Git state, then execute only the handoff's Next action and preserve all
stop conditions.
```
