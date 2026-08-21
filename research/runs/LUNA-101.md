# LUNA-101 umbrella tracker

- Integration branch: `integration/LUNA-101-academic-discovery`
- Batch branch: `agent/LUNA-101-01-academic-batch`
- Draft umbrella PR: [#8](https://github.com/jhg6636/autotrade-lab/pull/8)
- Baseline commit: `6dcd9ef` (`main` after LUNA-100-3-1)
- Target: 80 usable sources and 30 usable distinct hypotheses or explicit variants
- Current usable sources: 1
- Current usable hypotheses/variants: 1
- Incomplete sources: 12
- Inaccessible sources: 0
- Canonical records modified: false
- Automatic relation merge: false

## Batch ledger

| Batch | PR | Sources inspected | Usable sources | Usable hypotheses | Result |
| --- | --- | ---: | ---: | ---: | --- |
| Reviewed pilot baseline | [#5](https://github.com/jhg6636/autotrade-lab/pull/5) | 5 | 1 | 1 | accepted baseline |
| LUNA-101-01 | Draft sub-PR pending | 9 new source records / 8 hypotheses | 1 | 1 | Eight NBER records plus one separate NBER Reporter provenance record; Reporter rule usable, remaining records incomplete |

## Preserved blockers and ambiguities

- Twelve source records do not expose complete entry, exit, and sizing rules. They remain
  incomplete and do not count toward the completion target.
- The usable arXiv record is a context-only BitMEX Scenario 1 ADF variant; exact fees and residual
  rounding remain unspecified.
- No source rule may be reconstructed from a title, abstract, chart, or claimed result.
- Batch LUNA-101-01 inspected eight new unique NBER records (w20660, w5375, w24748, w7835,
  w14500, w6553, w16942, w18169) plus one separate NBER Reporter source. The Reporter source
  supports one usable monthly currency-momentum hypothesis; the paper landing source w16942
  remains separate and incomplete. The other records remain incomplete. No ranking or evidence
  score was assigned.

## Next batch

Next batch should continue from the latest integration branch, inspect at most 20 new unique public
academic, replication, or robustness candidates, and preserve any truthful shortfall.
