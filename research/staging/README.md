# Discovery staging

This directory is a non-canonical holding area for validated JSONL captures. It is intentionally
separate from `research/strategies/`. The aggregate command is dry-run only and never edits
canonical records.

The directory classes have different purposes:

- `fixtures/` contains synthetic shape and failure fixtures. They never count toward discovery
  targets.
- `pilot/` contains the reviewed public-source LUNA-101 and LUNA-104 baseline. These are real
  captures, but only records whose status is `usable` count toward a usable-source or hypothesis
  target.
- `collection/` is created on each lane's integration branch. Initialization moves that lane's
  accepted pilot files into its collection directory so the lane has one aggregate input and no
  duplicated source IDs.

Each collection lane may add `sources.jsonl`, `hypotheses.jsonl`, `inaccessible.jsonl`,
`relations.jsonl`, and `execution_audit.jsonl`. Collection remains research-only: it does not
authorize live orders, backtests, optimization, ranking, automatic relation merges, or canonical
promotion.

Reference rules are strict: `source_id` is unique within `sources.jsonl`; hypothesis
`source_ids` must resolve to a source capture; `inaccessible.source_id` must resolve to a source;
relation endpoints and execution-audit `hypothesis_id` values must resolve to hypothesis
records. Duplicate IDs and dangling references fail the aggregate before any discovery report is
written.

The branch, PR, batch-size, counting, and merge rules are defined in
`docs/DISCOVERY_PR_WORKFLOW.md`.
