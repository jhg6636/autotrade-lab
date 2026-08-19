# LUNA-101 preparation handoff

## Scope and stop gate

This is a preparation artifact only. No paper, replication, source, or strategy record is
collected in this task. Execution may begin only after user approval and must stop when any
required detail is inaccessible, paywalled, ambiguous, or not falsifiable. No credentials,
paywall bypass, paid dataset, ranking, evidence score, backtest, optimization, or strategy code
is allowed.

Starting commit: `396356f` (`origin/main`, latest known remote main at preparation time).
Finished commit: `c503cd5`.

## Collection target

- At least 80 usable source records.
- At least 30 distinct hypotheses or explicit parameter/execution variants.
- Positive, negative, and replication results enter the same flat pool.
- Source type is provenance only; it must never become a priority, confidence, authority, or
  evidence score.

## Allowed source lanes

Use only retrievable public material from journal sites, NBER, SSRN, arXiv, Google Scholar
citation trails, and replication papers. A citation trail is a discovery aid, not evidence by
itself; the cited paper or an accessible metadata page must be recorded.

Suggested order:

1. Replication and robustness papers that state an exact rule or testable specification.
2. Original journal/NBER/SSRN/arXiv papers with formulas, sample construction, and timing.
3. Citation-trail follow-ups, including negative or failed replications.
4. Accessible preprints or author manuscripts when the version and date are clear.

## Per-source capture contract

Every source capture must include:

- stable source ID and retrievable URL;
- title, author(s), publication year/date when known, access date, language, and `source_type`;
- a short claim summary, with any return/performance claim explicitly labelled `unverified`;
- exact entry rule, exit rule, sizing rule, universe, timeframe, and required data, or an
  explicit `unknown`/`inaccessible` marker;
- sample period, rebalance timing, signal lag, costs, and exclusions when stated;
- ambiguity and missing-detail notes;
- whether the source is original, replication, negative result, or follow-up, as neutral
  provenance metadata.

Do not reconstruct a rule from a title, abstract, chart, or claimed result. If the rule cannot
be converted into a falsifiable hypothesis, keep it as `incomplete` in the work log and do not
count it toward the 80 usable sources or 30 hypotheses target.

## Hypothesis and variant policy

- Exact repost or materially identical specification: one candidate record with an additional
  source candidate; never copy the same hypothesis as a new ranked item.
- Parameter change (for example, lookback or rebalance interval): preserve as a `variant_of`
  candidate with field-level reasons.
- Execution/data/universe change: preserve as a variant when the mechanism remains the same.
- Different mechanism or insufficient specification: `related_to` or `insufficient_information`;
  do not merge.
- All relation suggestions remain dry-run review artifacts; no automatic merge.

## Proposed folder structure

```text
research/
  discovery/
    academic/
      sources.jsonl              # one normalized source capture per line
      hypotheses.jsonl           # source-linked hypotheses/variants
      inaccessible.jsonl         # URLs/details blocked or incomplete
      relations.jsonl            # duplicate/variant/related suggestions
      README.md                  # lane-specific provenance notes
  runs/
    LUNA-101-prep.md
    LUNA-101.md                  # created only when execution is approved
    LUNA-101-dry-run.json
```

Canonical `research/strategies/*.json` must remain untouched during collection staging. A
promotion/import step, if later approved, must validate records and show a diff before changing
canonical data.

## Execution checklist

- [ ] User approval recorded; scope and date window fixed.
- [ ] Source ledger initialized with access date and URL status.
- [ ] Each source passes URL retrievability and metadata completeness checks.
- [ ] Exact rules are transcribed only when stated; otherwise marked incomplete/inaccessible.
- [ ] All claims labelled as unverified text claims; no measured result is imported.
- [ ] Every hypothesis links to one or more source IDs and has field-level ambiguity notes.
- [ ] Duplicate/variant/related dry-run report generated with reasons.
- [ ] Counts reach 80 usable sources and 30 hypotheses/variants, or a blocker report explains the
  shortfall.
- [ ] Schema validation, pytest, Ruff, and diff checks pass.
- [ ] Stop at Gate B input preparation; do not backtest or rank.

## Acceptance and blockers

Acceptance requires the targets, source fields, relation report, and validation checks above.
Paywalled or inaccessible details remain explicitly inaccessible. The smallest next action for
an access blocker is to ask the user whether an openly retrievable alternate version is allowed;
never bypass access controls or infer missing rules.
