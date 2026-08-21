# LUNA-101 umbrella tracker

- Integration branch: `integration/LUNA-101-academic-discovery`
- Draft umbrella PR: pending creation
- Baseline commit: `6dcd9ef` (`main` after LUNA-100-3-1)
- Target: 80 usable sources and 30 usable distinct hypotheses or explicit variants
- Current usable sources: 1
- Current usable hypotheses/variants: 1
- Incomplete sources: 4
- Inaccessible sources: 0
- Canonical records modified: false
- Automatic relation merge: false

## Batch ledger

| Batch | PR | Sources inspected | Usable sources | Usable hypotheses | Result |
| --- | --- | ---: | ---: | ---: | --- |
| Reviewed pilot baseline | [#5](https://github.com/jhg6636/autotrade-lab/pull/5) | 5 | 1 | 1 | accepted baseline |

## Preserved blockers and ambiguities

- Four public landing-page records do not expose complete entry, exit, and sizing rules. They
  remain incomplete and do not count toward the completion target.
- The usable arXiv record is a context-only BitMEX Scenario 1 ADF variant; exact fees and residual
  rounding remain unspecified.
- No source rule may be reconstructed from a title, abstract, chart, or claimed result.

## Next batch

Run `LUNA-101-01` from the latest integration branch. Inspect at most 20 new unique public
academic, replication, or robustness source candidates. Aim for at least eight usable sources and
five usable hypotheses or explicit variants, but preserve a truthful shortfall. Include positive,
negative, and replication findings without ranking them. Update this tracker and the umbrella PR,
then open the batch PR against `integration/LUNA-101-academic-discovery`.
