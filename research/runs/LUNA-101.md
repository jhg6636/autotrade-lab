# LUNA-101 umbrella tracker

- Integration branch: `integration/LUNA-101-academic-discovery`
- Closeout branch: `agent/LUNA-101-coverage-closeout`
- Draft umbrella PR: [#8](https://github.com/jhg6636/autotrade-lab/pull/8)
- Baseline commit: `6dcd9ef` (`main` after LUNA-100-3-1)
- Completion: 30 usable hypotheses, complete usable-source linkage, and local coverage audit
- Status: discovery complete pending closeout PR and final umbrella review
- Current usable sources: 26
- Current usable hypotheses/variants: 35
- Incomplete sources: 53
- Inaccessible sources: 1
- Canonical records modified: false
- Automatic relation merge: false

## Batch ledger

| Batch | PR | Sources inspected | Usable sources | Usable hypotheses | Result |
| --- | --- | ---: | ---: | ---: | --- |
| Reviewed pilot baseline | [#5](https://github.com/jhg6636/autotrade-lab/pull/5) | 5 | 1 | 1 | accepted baseline |
| LUNA-101-01 | [#10 merged](https://github.com/jhg6636/autotrade-lab/pull/10) | 9 new source records / 8 hypotheses | 1 | 1 | Eight NBER records plus one separate NBER Reporter provenance record; Reporter rule usable, remaining records incomplete |
| LUNA-101-02 | [#11 merged](https://github.com/jhg6636/autotrade-lab/pull/11) | 6 new source records / 9 hypotheses | 1 | 3 | Six public arXiv candidates appended; classical, w=0.5, and w=1 TSMOM rules are usable; five non-TSMOM candidates plus the learned CPD/DMN record remain incomplete |
| LUNA-101-03 | [#12 merged](https://github.com/jhg6636/autotrade-lab/pull/12) | 20 admitted audited inputs / 23 hypotheses | 3 | 6 | Coordinator review and remote checks passed; six disclosed trend overflow leads are excluded from every record, count, and status decision |
| LUNA-101-04 | [#13 merged](https://github.com/jhg6636/autotrade-lab/pull/13) | 20 audited inputs / 22 hypotheses | 14 | 15 | Independent coordinator review passed after exposure/status corrections; one inaccessible Halloween source retained without inferred rule |
| LUNA-101-05 | [#14 merged](https://github.com/jhg6636/autotrade-lab/pull/14) | 20 audited inputs / 28 hypotheses | 6 | 9 | Independent coordinator review passed after adversarial correction; uncapped context exposure is preserved only as explicit null bounds, while learned/toolkit/underspecified and signal-study records remain incomplete |

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
- LUNA-101-04 retains the blocked AER Halloween source as inaccessible, partial indexed international seasonality and the index-weight event study as incomplete, and all historical long/short rules as context-only. No ranking, backtest, canonical promotion, or automatic relation merge occurred.
- Coordinator correction keeps leveraged profiles only context-only (boundary 1.5, conditional 2, smoothing 5), fixes cash-merger long-only exposure and RAIM sizing, and applies deterministic-set status policy; the Chinese J/K grid is incomplete.
- LUNA-101-05 preserves learned TRA/A3C artifacts, generic configurable frameworks, missing-sizing
  technical-rule studies, unresolved Donchian/JSE exit parameters, BLL signal-return studies, and the
  performance-labelled BTC example as incomplete. IMC is explicitly winner-minus-loser after
  pinned-code inspection. Sepp normalized-sign TSMOM and Baltas record only source-stated uncapped
  context exposure using null bounds; Baltas does not increase underlying idea weight.

## Coverage closeout

The [local coverage audit](LUNA-101-coverage-audit.md) confirms 35 usable hypotheses across 13
families, three markets, and seven timeframe tags. All 35 link only to existing usable sources.
Concentration and sparse cells are documented rather than converted into automatic collection work.
There is no next generic discovery batch.
