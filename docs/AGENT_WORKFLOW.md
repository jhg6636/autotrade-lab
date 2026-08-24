# Agent orchestration and continuity

This workflow removes manual foreground-model switching from normal repository work. One
coordinator keeps the active objective and dispatches bounded sub-agent tasks. The research
protocol and discovery workflow remain authoritative for domain rules and branch topology.

## Roles and gates

| Role | Default model | Owns | Must not do alone |
| --- | --- | --- | --- |
| Coordinator/reviewer | Sol | goal, plan, task packets, adversarial review, user updates, merge recommendation | trust summaries without inspecting the diff |
| Collector | Luna | bounded public-source retrieval and literal field transcription | invent rules, promote ambiguous records, change classifier/schema semantics |
| Implementer | Terra | code, tests, deterministic artifacts, tracker synchronization | expand scope, weaken safety gates, self-approve semantic ambiguity |

Use capability and observed performance rather than the model label when assigning work. The
coordinator may implement a small, already-understood correction directly when another handoff
would cost more than the change.

## Work state machine

```text
planned -> delegated -> implemented -> reviewed -> verified -> committed -> pushed/PR -> merged
                         ^              |
                         |-- rework ----|
```

- `planned`: objective, permitted scope, checks, and stop conditions are explicit.
- `delegated`: one agent owns a bounded, non-overlapping file set.
- `implemented`: the agent reports the commit/diff and check results.
- `reviewed`: the coordinator inspects source evidence, code paths, counts, and adversarial cases.
- `verified`: independent checks pass and findings are resolved.
- `committed`: the worktree is clean at the recorded commit.
- `pushed/PR`: exact base/head and remote state are recorded.
- `merged`: only the authorized target branch changed; the handoff points to the next action.

A failed review returns to `implemented` with concrete findings. Do not create a new batch while
the current batch has unresolved P1/P2 findings.

## Task packet template

```markdown
Task ID:
Objective:
Base branch and commit:
Allowed files:
Required source material:
Procedure:
Completion conditions:
Verification commands:
Stop conditions:
Forbidden actions:
Expected handoff fields:
```

The packet must name exact evidence for semantic work. For collection, it must state the maximum
number of new sources and whether web access is permitted. For code, it must include positive and
negative regression cases.

## Review checklist

The coordinator checks more than the happy path:

1. Entry/exit direction, long/short side, polarity, operand order, target exposure, and timeframe.
2. Parameter variants versus genuinely different mechanisms.
3. Source status versus every source-linked hypothesis status.
4. Exact batch deltas as well as cumulative totals.
5. Tracker, run report, aggregate artifact, branch, commit, and PR agreement.
6. Determinism, canonical-file isolation, and absence of credentials or live-order changes.
7. At least one adversarial regression for every new mechanism classifier.

Passing tests do not close a review finding when the missing case is not covered by those tests.

## Goal and cross-device continuity

Runtime `/goal` state is convenient but is not stored in Git. Mirror it in
`research/runs/HANDOFF.md`. At the beginning of a new session or on another device:

1. read `AGENTS.md` and `research/runs/HANDOFF.md`;
2. fetch remote state and verify the recorded branch/commit rather than assuming it exists;
3. recreate the runtime goal from `Active objective` and `Completion condition`;
4. run the handoff's read-only verification commands;
5. execute only `Next action`, updating the handoff when state changes.

The handoff must contain no secrets or device-specific paths. Use repository-relative paths and
stable GitHub links.

## User interaction

The coordinator gives compact progress updates and asks the user only for a consequential choice,
new authority, credentials through an approved secret mechanism, or a genuine blocker. Routine
model selection, sub-agent dispatch, re-review, and rework stay inside the coordinator workflow.

Batch merges into an integration branch may follow the authority already granted in
`docs/DISCOVERY_PR_WORKFLOW.md`. Merging an integration branch into `main`, starting post-Gate-B
data collection, or enabling any trading capability still requires the applicable explicit gate.
