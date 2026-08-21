# LUNA-104 umbrella tracker

- Integration branch: `integration/LUNA-104-korean-discovery`
- Draft umbrella PR: [#9](https://github.com/jhg6636/autotrade-lab/pull/9)
- Baseline commit: `6dcd9ef` (`main` after LUNA-100-3-1)
- Target: 80 usable sources and 30 usable hypotheses or explicit variants
- Current usable sources: 0
- Current usable hypotheses/variants: 0
- Incomplete sources: 5
- Inaccessible sources: 0
- Canonical records modified: false
- Automatic relation merge: false

## Batch ledger

| Batch | PR | Sources inspected | Usable sources | Usable hypotheses | Result |
| --- | --- | ---: | ---: | ---: | --- |
| Reviewed pilot baseline | [#5](https://github.com/jhg6636/autotrade-lab/pull/5) | 5 | 0 | 0 | accepted context baseline |

## Preserved blockers and ambiguities

- The five KRX/KCMI baseline records provide product, market, and behavioral context but do not
  expose complete entry, exit, and sizing rules. They remain incomplete and do not count toward
  the completion target.
- Korean execution feasibility is not inferred from a paper, institutional page, or blog.
- Korean equity and ETF executable applications must remain long-only with nonnegative exposure;
  historical short legs remain context-only.

## Next batch

Run `LUNA-104-01` from the latest integration branch. Inspect at most 20 new unique public Korean
source candidates, prioritizing openly retrievable papers, finance-society material, broker
education, and public practitioner descriptions that state falsifiable rules rather than adding
more market-regulation context. Aim for at least eight usable sources and five usable hypotheses
or explicit variants, but preserve a truthful shortfall. Retain Korean metadata, update this
tracker and the umbrella PR, then open the batch PR against
`integration/LUNA-104-korean-discovery`.
