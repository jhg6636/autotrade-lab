## Objective

- Task/batch ID:
- Required base branch:
- Starting commit:
- Finished content commit:

## Scope

- Sources inspected:
- Sources added (usable/incomplete/inaccessible):
- Hypotheses added (usable/incomplete/inaccessible):
- Files intentionally changed:
- Canonical strategy/index changed: no
- Automatic relation merge performed: no

## Research integrity

- [ ] Rules, timing, costs, sizing, universe, and required data are transcribed only when stated.
- [ ] Claimed performance remains labelled `unverified`.
- [ ] Source type is provenance only; no hierarchy or evidence score was introduced.
- [ ] Parameter/execution variants have field-level reasons.
- [ ] Direction, polarity, long/short side, operand order, and target exposure were adversarially checked.
- [ ] Source and linked-hypothesis statuses are consistent.
- [ ] Batch deltas and cumulative tracker counts agree with the ledgers and aggregate.
- [ ] No backtest, optimization, ranking, canonical promotion, credential, Toss call, or order was added.

## Verification

```text
.venv/bin/python research/aggregate_staging.py --staging-dir <lane-dir> --report <report-a>
.venv/bin/python research/aggregate_staging.py --staging-dir <lane-dir> --report <report-b>
cmp <report-a> <report-b>
.venv/bin/pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
git diff --check
```

- [ ] Aggregate outputs are byte-identical.
- [ ] Schema/reference validation passes.
- [ ] Tests and lint pass.
- [ ] Canonical strategy/index diff is empty.
- [ ] Coordinator inspected the actual diff and negative regression cases.

## Preserved ambiguity and blockers

- Ambiguities:
- Inaccessible material:
- Remote/CI blockers:
- Next action:
