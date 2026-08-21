# Stage 1 discovery PR workflow

This workflow keeps large discovery lanes reviewable without treating source provenance as a
quality rank. It applies first to LUNA-101 and LUNA-104 and may be reused for LUNA-102, LUNA-103,
and LUNA-105 after their preparation handoffs are approved.

## Branch and PR topology

Each lane has one long-lived integration branch and one Draft umbrella PR targeting `main`:

| Lane | Integration branch | Umbrella PR target |
| --- | --- | --- |
| LUNA-101 | `integration/LUNA-101-academic-discovery` | `main` |
| LUNA-104 | `integration/LUNA-104-korean-discovery` | `main` |

Batch branches use `agent/<lane>-<two-digit-batch>-<short-name>`, start from the latest lane
integration branch, and open a PR back to that integration branch. Only one batch PR per lane may
be open at a time because each batch appends to the same JSONL ledgers. LUNA-101 and LUNA-104 may
run independently in parallel.

GitHub does not provide a native parent/child PR relation. The umbrella PR body is the source of
truth for links to merged batch PRs, cumulative counts, preserved blockers, and the next batch.

## Integration initialization

The first commit on an integration branch must:

1. move the lane's accepted files from `research/staging/pilot/<lane>/` to
   `research/staging/collection/<lane>/` without changing record content;
2. add `research/runs/<lane>.md` using the umbrella tracker template below;
3. run the aggregate twice and confirm byte-identical reports;
4. confirm `automatic_merge=false`, `canonical_records_modified=false`, and no diff under
   `research/strategies/` or `research/strategy_index.csv`;
5. open a Draft umbrella PR to `main`.

The reviewed pilot is the lane baseline, but only `usable` source and hypothesis records count
toward a target. Incomplete and inaccessible records remain in the flat pool and are reported
without being promoted or discarded.

## Batch contract

Every batch must:

1. inspect no more than 20 new unique source candidates so the PR remains reviewable;
2. append only retrievable public material or explicitly marked inaccessible records;
3. transcribe exact entry, exit, sizing, universe, timing, cost, and data rules only when the
   source states them;
4. retain positive, negative, replication, institutional, and community claims in one flat pool;
5. label claimed performance as `unverified` text and never import it as a measured result;
6. preserve parameter, execution, data, and universe variants with field-level relation reasons;
7. regenerate dry-run relation and lane audit artifacts without automatically merging records;
8. update the umbrella tracker and PR body with cumulative counts and the next batch;
9. stop before strategy code, ranking, optimization, backtesting, canonical promotion, or orders.

A batch should aim to add at least eight `usable` sources and five usable hypotheses or explicit
variants. A truthful shortfall is not a batch failure: record the inaccessible or underspecified
sources, explain the shortfall, and continue with the next bounded batch. No rule may be invented
to satisfy a count.

For LUNA-104, executable Korean equity and ETF applications must remain long-only, nonnegative,
and daily or one-minute. Historical short legs may be retained only as `context_only`. Toss is the
intended future broker boundary, but collection does not call Toss or use credentials.

## Batch acceptance and merge authority

Before a batch PR is merged into its integration branch, Luna must verify:

- schema and reference validation passes;
- exact source URLs and IDs are unique;
- two aggregate runs produce byte-identical reports;
- `.venv/bin/pytest -q`, `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`, and
  `git diff --check` pass;
- no canonical strategy/index, strategy implementation, credential, order, or backtest file is
  changed;
- the PR base is the correct integration branch and the umbrella tracker is updated.

Luna may merge a batch PR into its integration branch when every check passes and there is no
ambiguous scope decision. Luna must stop for Sol review if a source requires inferred rules, a
relation is materially ambiguous, a constraint would change, or a batch touches canonical data.
The integration branch must never be merged automatically into `main`.

## Umbrella completion

The LUNA-101 umbrella is ready for final Sol review at 80 usable sources and 30 usable distinct
hypotheses or explicit variants. The LUNA-104 umbrella is ready at 80 usable sources and 30 usable
hypotheses or variants with Korean metadata retained and the long-only execution audit passing.

At completion, Sol verifies the full lane, unresolved ambiguities, deterministic reports, exact
target counts, and main-branch mergeability. Only then may the Draft umbrella PR be marked ready
and merged to `main`. Canonical promotion remains a separate post-discovery decision.

## Umbrella tracker template

```markdown
# <lane> umbrella tracker

- Integration branch:
- Draft umbrella PR:
- Baseline commit:
- Target:
- Current usable sources:
- Current usable hypotheses/variants:
- Incomplete sources:
- Inaccessible sources:
- Canonical records modified: false
- Automatic relation merge: false

## Batch ledger

| Batch | PR | Sources inspected | Usable sources | Usable hypotheses | Result |
| --- | --- | ---: | ---: | ---: | --- |

## Preserved blockers and ambiguities

## Next batch
```
