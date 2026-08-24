# Agent operating contract

This file is the entry point for any coding agent continuing work in this repository. Read it
before editing, then follow the linked domain documents. Session state, model selection, and chat
history are not sources of truth.

## Sources of truth

Use the following order when instructions overlap:

1. the user's current request;
2. this file;
3. `research/runs/HANDOFF.md` for the active objective and repository state;
4. `docs/AGENT_WORKFLOW.md` for delegation, review, and continuity;
5. `docs/RESEARCH_PROTOCOL.md` and `docs/DISCOVERY_PR_WORKFLOW.md` for research rules;
6. the task-specific plan and run report.

Do not copy mutable counts or branch state into additional documents. Update the tracker and
handoff instead.

## Operating model

Keep one coordinator responsible for the active goal. The user should not need to switch the
foreground model between implementation and review.

- **Coordinator/reviewer:** owns the plan, delegates bounded work, runs adversarial review,
  decides whether completion criteria are met, and reports to the user. Prefer the strongest
  reasoning model available (currently Sol).
- **Collector:** retrieves public sources and transcribes only stated facts into the required
  fields. Prefer a fast model (currently Luna). It must not decide novel schema or relation
  semantics.
- **Implementer:** changes code, tests, schemas, aggregate output, and synchronized documentation
  from an explicit task packet. Prefer a balanced coding model (currently Terra).

These are capability roles, not permanent model identities. If a named model is unavailable, use
another model for the role while preserving the same review boundary.

## Delegation rules

Every delegated task must state the exact objective, base branch/commit, allowed files, procedure,
completion checks, and stop conditions. Agents sharing a worktree must not edit overlapping files
concurrently. The coordinator reviews the actual diff and reruns relevant checks; a sub-agent's
summary is never sufficient evidence by itself.

Collection and mechanical transcription may be delegated to the collector. Code changes,
status/count decisions, schema changes, relation logic, and cross-file synchronization go to the
implementer or coordinator. Direction, polarity, timing, target exposure, and source-to-hypothesis
status are mandatory adversarial-review dimensions.

## Safety and scope

- Never place a real order or enable live trading.
- Never commit credentials, tokens, account data, paid content, or machine-specific secret paths.
- Do not bypass paywalls, accept licenses, purchase data, or change repository visibility.
- During Stage 1 discovery, do not rank, optimize, backtest, promote canonical records, or
  automatically merge relation suggestions.
- Korean-listed stock and ETF execution candidates are long-only and limited to daily or
  one-minute horizons. Historical short legs may remain context-only.
- Stop for the user when work needs credentials, paid data, a scope change, a main-branch merge,
  or another consequential external decision.

## Completion and continuity

Before declaring a repository task complete, run the task-specific checks plus, when applicable:

```text
.venv/bin/pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
git diff --check
```

For discovery batches, also validate schemas/references, run the aggregate twice, compare the
outputs byte-for-byte, and confirm canonical strategy/index files are unchanged.

After every meaningful commit, review decision, PR/merge, or blocker change, update
`research/runs/HANDOFF.md`. Keep its next action singular and executable. A new session should be
able to recreate its runtime goal from that file without relying on prior chat history.
