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
- Last reviewed research commit: `66a3708` (`LUNA-101-02: fix TSMOM variants and counts`)
- Required PR base: `integration/LUNA-101-academic-discovery`
- Matching remote batch branch: `origin/agent/LUNA-101-02-academic-batch`
- Draft batch PR: `#11`, targeting `integration/LUNA-101-academic-discovery`
- Umbrella PR: `#8` targeting `main`
- Worktree at last review: clean
- Canonical strategy/index modified: false
- Automatic relation merge: false

The checked-out `git rev-parse HEAD` is authoritative for the current documentation commit; do not
rewrite this handoff merely to embed its own commit hash.

Current aggregate:

- sources: 20 total, 3 usable, 17 incomplete, 0 inaccessible;
- hypotheses: 22 total, 5 usable, 17 incomplete, 0 inaccessible;
- suggestions: 91.

## Open review findings

1. `src/autotrade_lab/research/discovery.py` recognizes any TSMOM/`sgn(...)` rule as the same
   mechanism without preserving signal polarity. A direct check classified
   `X=sgn(r[t-252,t])` and `X=-sgn(r[t-252,t])` as `variant_of`; the latter must be a different
   mechanism/`related_to`. Add polarity/formula-direction identity and a negative regression test.
2. LUNA-101-02 added 6 source records and 9 hypothesis records (collection hypotheses increased
   from 13 to 22), but `research/runs/LUNA-101.md` says 6 hypotheses.
3. `research/runs/LUNA-101-02.md` says four remaining candidates are incomplete; there are five
   non-TSMOM candidates plus the incomplete learned CPD/DMN hypothesis. Its usable-hypothesis list
   also omits the `w=0.5` and `w=1` variants.

Existing checks pass (`67 passed`, Ruff/format/diff clean, deterministic aggregate), but they do
not cover the polarity counterexample. The batch is not merge-ready while these findings remain.

## Next action

Implement the three open findings on the current batch branch, add both positive parameter-variant
and negative polarity-reversal tests, regenerate the aggregate twice, update this handoff to the
new commit and resolved state, then run independent coordinator review before push/PR creation.

## Resume instruction

```text
Read AGENTS.md, docs/AGENT_WORKFLOW.md, research/runs/HANDOFF.md, and the linked research workflow.
Recreate the active LUNA-101 goal. Keep the coordinator in the foreground, delegate bounded
implementation to Terra and mechanical collection to Luna, and do not ask the user to switch
models. Verify the recorded Git state, then execute only the handoff's Next action and preserve all
stop conditions.
```
