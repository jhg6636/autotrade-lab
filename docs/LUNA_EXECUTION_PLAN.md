# Luna execution plan

This document is an executable backlog for Luna. Luna must work on one task ID at a time,
respect dependencies, preserve every source without ranking it, and stop at the stated gates.
Unless a task explicitly says otherwise, Luna may edit the repository, run local tests, and use
public read-only web sources. Luna must never place a real order, enable live trading, purchase a
dataset, accept a license, publish credentials, or change repository visibility.

## Global operating contract

For every task Luna must:

1. start from the latest `main` and record the starting commit, except a Stage 1 batch that must
   start from the latest lane integration branch under `docs/DISCOVERY_PR_WORKFLOW.md`;
2. read `README.md`, `docs/RESEARCH_PROTOCOL.md`, and this file;
3. create a branch named `agent/<task-id>-<short-name>`; Stage 1 batch IDs include a two-digit
   batch number;
4. make only changes required by that task;
5. add or update tests for executable code;
6. run `.venv/bin/pytest -q`, `.venv/bin/ruff check .`, and `git diff --check`;
7. write `research/runs/<task-id>.md` using the run-report template below;
8. commit with `<task-id>: <outcome>` and open a draft PR against the task's required base;
9. stop at a decision gate instead of silently expanding scope.

If a required command, credential, paid source, ambiguous license, or user decision blocks the
task, Luna records the exact blocker and the smallest next action. It must not invent data or
silently substitute a different dataset.

## Required run report

```markdown
# <task-id> run report

- Starting commit:
- Finished commit:
- Started/finished at (KST):
- Inputs inspected:
- Sources added:
- Files changed:
- Commands run:
- Test results:
- Assumptions:
- Ambiguities preserved:
- Blockers:
- Recommended next task:
```

## Stage 0 — freeze the research substrate

### LUNA-001: Define the strategy-record schema

**Objective:** Create a machine-readable, source-neutral schema for one strategy idea.

**Inputs**

- `docs/RESEARCH_PROTOCOL.md`
- `src/autotrade_lab/catalog.py`
- Existing 35 catalog entries

**Procedure**

1. Add `research/schema/strategy.schema.json` using JSON Schema 2020-12.
2. Require: stable ID, canonical name, aliases, family, markets, asset direction, timeframe,
   source records, falsifiable hypothesis, entry rule, exit rule, sizing rule, required fields,
   execution assumptions, variants, ambiguities, and implementation status.
3. A source record must capture type, title, author/handle, URL, publication date when known,
   access date, language, and verbatim claim summary. `source_type` must not imply rank.
4. Represent Korean equities as `long_only`; reject a Korean-equity executable rule containing
   negative target exposure.
5. Add fixture records for one academic idea, one community idea, and one original observation.
6. Add a validator module and tests for valid, invalid, and long-only cases.

**Outputs**

- `research/schema/strategy.schema.json`
- `research/fixtures/strategies/*.json`
- `src/autotrade_lab/research/validation.py`
- tests

**Acceptance criteria**

- All three fixtures validate.
- Missing trading rules fail with a useful field path.
- Identical records differing only in source type both validate.
- A Korean-stock short target fails validation.
- Existing tests and lint pass.

**Stop conditions:** Do not migrate the full catalog in this task.

### LUNA-002: Migrate the existing catalog

**Depends on:** LUNA-001

**Objective:** Convert all existing catalog entries into schema-valid hypothesis records without
adding evidence scores or silently filling unknown details.

**Procedure**

1. Create one JSON file per canonical hypothesis under `research/strategies/`.
2. Preserve all current names, families, markets, hypotheses, and risks.
3. Use explicit `unknown`/ambiguity fields instead of guessing entry or exit rules.
4. Link implemented entries to their Python implementation.
5. Generate `research/strategy_index.csv` deterministically from JSON records.
6. Add checks for unique IDs, unique canonical slugs, valid implementation paths, and stable CSV
   generation.

**Acceptance criteria**

- No current catalog entry is lost.
- Generated index contains exactly one row per record.
- Two consecutive generations produce no diff.
- No authority, evidence, confidence, popularity, or priority score exists.

**Stop conditions:** Do not add newly discovered strategies yet.

### LUNA-003: Define discovery and deduplication mechanics

**Depends on:** LUNA-001

**Objective:** Make collection reproducible while retaining variants.

**Procedure**

1. Define normalized fingerprints from market, timeframe, signal inputs, entry, exit, and sizing.
2. Implement three relations: `duplicate`, `variant_of`, and `related_to`.
3. Exact reposts become additional sources on the same record.
4. Parameter or execution differences become variants, never overwritten duplicates.
5. Produce a dry-run report; no automatic merge may occur without an explicit flag.

**Acceptance criteria**

- Tests cover repost, parameter variant, and merely related strategy.
- Default command modifies no strategy records.
- Every suggested merge includes field-level reasons.

## Gate A — user review

After LUNA-001 through LUNA-003, stop and ask the user to review:

- whether the schema captures enough detail;
- whether deduplication preserves useful variants;
- whether the index is readable;
- whether source neutrality is visible in actual records.

No bulk research begins before Gate A approval.

## Stage 1 — broad, flat discovery

Run the following tasks independently after Gate A. Each task gathers ideas but does not rank,
backtest, or implement them. Every collected claim must link to a retrievable source or be marked
as an original observation.

LUNA-101 and LUNA-104 use the integration-branch, Draft umbrella PR, bounded-batch, counting, and
merge rules in `docs/DISCOVERY_PR_WORKFLOW.md`. Their batch PRs target the lane integration branch,
not `main`; only the completed umbrella PR targets `main`.

### LUNA-101: Academic and replication discovery

Search journal sites, NBER, SSRN, arXiv, Google Scholar citation trails, and replication papers.
Collect formulas, variants, negative results, and implementation details. Negative and positive
papers create or enrich hypotheses equally.

**Target:** at least 80 usable source records and 30 distinct/variant hypotheses.

### LUNA-102: Books, practitioners, and institutional research

Search systematic-trading books, author resources, AQR/Man/Research Affiliates and comparable
institutional publications, interviews, conference material, and practitioner notebooks.

**Target:** at least 60 usable sources and 25 hypotheses/variants.

### LUNA-103: Community, code, and video discovery

Search GitHub, TradingView public scripts/descriptions, QuantConnect examples, blogs, forums,
Reddit, Korean communities, podcasts, and videos. Record exact rules when available; preserve
vague claims as incomplete records rather than reverse-engineering them.

**Target:** at least 100 usable sources and 40 hypotheses/variants.

### LUNA-104: Korean-market discovery

Search RISS, DBpia/KCI metadata accessible without bypass, Korean finance societies, KRX,
KCMI, DART-related studies, Korean blogs/communities, and broker educational material.
Collect only long-only executable variants for Korean listed equities/ETFs; record short legs as
context but set them non-executable.

**Target:** at least 80 sources and 30 hypotheses/variants, with Korean-language metadata kept.

### LUNA-105: Crypto-native discovery

Search exchange documentation, protocol documentation, public research, GitHub, dashboards,
trader communities, and on-chain analytics descriptions for spot/perpetual strategies, funding,
basis, listings, liquidations, flows, and microstructure.

**Target:** at least 80 sources and 35 hypotheses/variants.

### Common acceptance criteria for LUNA-101…105

- Every record passes schema validation.
- Every source has an access date and type but no rank.
- Claimed returns are text claims, never imported as measured results.
- Paywalled/inaccessible details are marked inaccessible; no imagined rule is added.
- Duplicate reports and unresolved ambiguities are generated.
- No strategy code, optimization, or backtest is added.

## Stage 2 — synthesis without ranking

### LUNA-201: Catalog coverage audit

**Depends on:** LUNA-101…105

Create matrices by family, market, timeframe, required data, turnover class, and execution type.
Identify empty cells and conduct one supplemental discovery pass. Do not call a well-covered cell
better than a sparse cell.

### LUNA-202: Data-requirement matrix

**Depends on:** LUNA-201

For every hypothesis, enumerate required fields and minimum history. Map each field to potential
providers and distinguish Toss availability, exchange availability, public external data, paid
data, derived data, and unavailable data. Include point-in-time, corporate-action, survivorship,
timezone, licensing, retention, and redistribution requirements.

### LUNA-203: Executability audit

**Depends on:** LUNA-202

Determine whether each rule can be tested and later executed under project constraints:

- Korean stocks/ETFs: Toss Securities, long-only, daily or one-minute;
- crypto: spot/perpetual, long/short allowed;
- no ultra-low-latency dependency;
- no real orders;
- no privileged or manipulative behavior.

Use outcomes `ready_for_data`, `needs_external_data`, `ambiguous_rule`, `out_of_scope`, or
`blocked`. These are feasibility states, not profitability ranks.

## Gate B — user review

Stop with the following decision package:

- total unique hypotheses and variants;
- family/market/timeframe coverage matrix;
- unresolved ambiguity list;
- data fields and provider candidates;
- estimated storage, API traffic, paid-data decisions, and licensing risks;
- proposed first data collection batch, with rationale based on coverage and reuse rather than
  expected profit.

No bulk market-data collection begins before Gate B approval.

## Stage 3 — proposed first data work (not authorized yet)

These tasks are placeholders for discussion and must not run before Gate B.

### LUNA-301: Toss API capability probe

Use credentials only after the user supplies them through a secret mechanism. Make read-only
calls for auth, stock master, market calendar, daily candles, one-minute candles, current price,
orderbook, trades, rankings, indices, and investor trading. Record pagination, retention depth,
rate-limit headers, response schemas, missingness, and terms. Do not call account or order APIs.

### LUNA-302: Korean universe snapshots

Collect dated stock-master snapshots, listing state, warnings, calendars, and corporate-action
source mappings. Demonstrate that a past universe can be reconstructed before collecting broad
price history.

### LUNA-303: Crypto public-data probe

Use public endpoints/archive files only. Sample spot/perpetual candles, trades, funding, open
interest, instrument metadata, and listing events. Record venue clocks, symbol lifecycle, limits,
and gaps.

### LUNA-304: Storage proof of concept

Compare Parquet partitioning and a local analytical database on one bounded sample. Define raw,
normalized, and point-in-time layers; checksums; provenance; idempotent ingestion; and quality
reports. Do not select infrastructure based on benchmark speed alone.

## Recommended immediate dispatch

Dispatch only **LUNA-001** first. Review its schema and fixtures before LUNA-002 and LUNA-003.
This is intentionally narrow: a flawed record model multiplied across hundreds of sources is
more expensive to repair than delaying discovery by one short task.
