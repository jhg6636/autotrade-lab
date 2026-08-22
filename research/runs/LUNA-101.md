# LUNA-101 umbrella tracker

- Integration branch: `integration/LUNA-101-academic-discovery`
- Batch branch: `agent/LUNA-101-03-academic-batch`
- Draft umbrella PR: [#8](https://github.com/jhg6636/autotrade-lab/pull/8)
- Baseline commit: `6dcd9ef` (`main` after LUNA-100-3-1)
- Target: 80 usable sources and 30 usable distinct hypotheses or explicit variants
- Current usable sources: 6
- Current usable hypotheses/variants: 11
- Incomplete sources: 34
- Inaccessible sources: 0
- Canonical records modified: false
- Automatic relation merge: false

## Batch ledger

| Batch | PR | Sources inspected | Usable sources | Usable hypotheses | Result |
| --- | --- | ---: | ---: | ---: | --- |
| Reviewed pilot baseline | [#5](https://github.com/jhg6636/autotrade-lab/pull/5) | 5 | 1 | 1 | accepted baseline |
| LUNA-101-01 | [#10 merged](https://github.com/jhg6636/autotrade-lab/pull/10) | 9 new source records / 8 hypotheses | 1 | 1 | Eight NBER records plus one separate NBER Reporter provenance record; Reporter rule usable, remaining records incomplete |
| LUNA-101-02 | [#11 merged](https://github.com/jhg6636/autotrade-lab/pull/11) | 6 new source records / 9 hypotheses | 1 | 3 | Six public arXiv candidates appended; classical, w=0.5, and w=1 TSMOM rules are usable; five non-TSMOM candidates plus the learned CPD/DMN record remain incomplete |
| LUNA-101-03 | [#12](https://github.com/jhg6636/autotrade-lab/pull/12) | 20 admitted audited inputs / 23 hypotheses | 3 | 6 | Coordinator review passed at `e0fe32b`; Draft PR awaits remote checks; six disclosed trend overflow leads are excluded from every record, count, and status decision |

## Preserved blockers and ambiguities

- Seventeen source records do not expose complete entry, exit, and sizing rules. They remain
  incomplete and do not count toward the completion target.
- The usable arXiv record is a context-only BitMEX Scenario 1 ADF variant; exact fees and residual
  rounding remain unspecified.
- No source rule may be reconstructed from a title, abstract, chart, or claimed result.
- Batch LUNA-101-01 inspected eight new unique NBER records (w20660, w5375, w24748, w7835,
  w14500, w6553, w16942, w18169) plus one separate NBER Reporter source. The Reporter source
  supports one usable monthly currency-momentum hypothesis; the paper landing source w16942
  remains separate and incomplete. The other records remain incomplete. No ranking or evidence
  score was assigned.
- LUNA-101-03 preserved 17 incomplete sources and 17 incomplete hypotheses rather than infer
  missing boundaries, sizing, formulas, timing, or contradictory earnings thresholds. Its 20
  admitted full-text inputs are distinct from six disclosed trend overflow discovery leads, which
  are excluded from the lane entirely.

## Next batch

Verify PR `#12` checks, review threads, exact base/head, and mergeability before marking it ready.
