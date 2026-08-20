# LUNA-104 preparation handoff

## Scope and stop gate

This is a preparation artifact only. No Korean-market source, strategy, or canonical JSON record
is collected or changed here. Execution requires user approval. Never bypass a paywall, request
credentials, place an order, call a private API, backtest, optimize, rank, or assign evidence
scores. A source-level rule or market detail that is inaccessible or not falsifiable is recorded
as incomplete/inaccessible and collection continues; only a system-wide blocker stops the task.

Starting commit: `396356f` (`origin/main`, latest known remote main at preparation time).
Finished commit: `1f58125`.

## Collection target

- At least 80 usable source records.
- At least 30 distinct hypotheses or explicit variants.
- Korean-language titles, authors/organizations, dates, URLs, and claim summaries are retained.
- All ideas remain a flat pool regardless of source type or perceived authority.

## Allowed source lanes

Use only material accessible without bypass from RISS, DBpia/KCI metadata, Korean finance
societies, KRX, KCMI, DART-related studies, Korean blogs/communities, and broker educational
material. Record the exact access mode and whether the source contains metadata only or an exact
rule. Metadata-only items cannot be promoted to usable exact-rule hypotheses without an openly
retrievable specification.

Suggested order:

1. KRX/KCMI/finance-society material describing universes, signals, calendars, or testable rules.
2. RISS/DBpia/KCI accessible metadata and openly available abstracts/full text.
3. DART-related event studies only when the event timestamp and selection rule are stated.
4. Korean broker education and public blogs/communities for explicit rule variants, retaining
   their Korean wording and ambiguity notes.

## Per-source capture contract

Every source record must include stable ID, URL, Korean title where available, author/handle or
organization, accessed date, `language` (preserve `ko`), `source_type`, and a neutral claim
summary. Also capture:

- exact universe and listing-state rule;
- daily or one-minute timeframe only;
- entry, exit, signal timing, rebalance, and sizing rules;
- required fields and provider/source dependencies;
- taxes, fees, slippage, liquidity, price adjustment, corporate actions, and point-in-time
  details when stated;
- ambiguity, inaccessible detail, and survivorship/look-ahead concerns;
- claimed returns or win rates only as text explicitly labelled `unverified`.

Do not infer Korean execution feasibility from a paper or blog alone. If the rule is not
falsifiable, record it as incomplete and exclude it from the usable/hypothesis target counts.

## Korean execution constraints

- Executable Korean equity/ETF applications must be `long_only` with nonnegative exposure and
  must satisfy the existing JSON Schema validator.
- Toss Securities is the intended broker boundary; this prep does not call the API or use
  credentials.
- Stock/ETF horizons are daily or one-minute. Ultra-low-latency, streaming-only, or unavailable
  data dependencies are marked `out_of_scope` or `needs_external_data`, not guessed.
- A historical short leg may be retained as context-only (`execution_scope: context_only`), but
  it must never become an executable Korean application or receive a negative executable target.
- Crypto or non-Korean markets may be recorded only when they are genuinely part of the source
  hypothesis; this task's executable target is Korean listed equities/ETFs.

## Proposed folder structure

```text
research/
  discovery/
    korean/
      sources.jsonl              # Korean metadata and source provenance
      hypotheses.jsonl           # source-linked flat hypotheses/variants
      inaccessible.jsonl         # paywall/access/detail blockers
      relations.jsonl            # dry-run duplicate/variant/related output
      execution_audit.jsonl      # long-only/Toss/timeframe checks
      README.md                  # Korean terminology and access notes
  runs/
    LUNA-104-prep.md
    LUNA-104.md                  # created only when execution is approved
    LUNA-104-dry-run.json
```

Staging files are not canonical strategy records. A later promotion step must validate every
record, show source-linked diffs, and keep short rules context-only. No `research/strategies/*.json`
file is modified by this preparation task.

## Execution checklist

- [ ] User approval and collection date window recorded.
- [ ] Source ledger initialized with Korean metadata and URL accessibility status.
- [ ] At least 80 usable accessible source records and 30 hypotheses/variants targeted.
- [ ] Exact rules copied only when stated; inaccessible details remain marked inaccessible.
- [ ] Daily/one-minute and Toss data requirements recorded per hypothesis.
- [ ] Korean executable applications validated as long-only with nonnegative exposure.
- [ ] Short legs explicitly marked context-only and excluded from executable candidates.
- [ ] Point-in-time universe, delistings, corporate actions, taxes, fees, and liquidity notes
  captured where stated.
- [ ] Duplicate/variant/related dry-run report generated with field-level reasons.
- [ ] Schema validation, pytest, Ruff, and diff checks pass.
- [ ] Stop before any backtest, ranking, strategy code, API credential use, or Gate B decision.

## Acceptance and blockers

Acceptance requires 80 usable sources, 30 hypotheses/variants, Korean metadata retention, a
long-only execution audit, and unresolved-access reports. Paywalled or bypass-restricted material
is recorded as inaccessible and excluded from exact-rule counts while collection continues. The
smallest next action is to log the source and continue; only a system-wide validator, storage,
authorization, or collection-runner blocker stops the task. Do not guess missing rules.
