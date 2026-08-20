# Discovery staging

This directory is a non-canonical holding area for validated JSONL captures. It is intentionally
separate from `research/strategies/`. `luna-101` and `luna-104` contain synthetic fixtures only;
they are not real sources and must not be counted toward discovery targets. The aggregate command
is dry-run only and never edits canonical records.

Each lane may later add `sources.jsonl`, `hypotheses.jsonl`, `inaccessible.jsonl`,
`relations.jsonl`, and `execution_audit.jsonl`. Five synthetic source/candidate records per lane
are reserved as a pilot shape; no live collection is authorized by this fixture.
