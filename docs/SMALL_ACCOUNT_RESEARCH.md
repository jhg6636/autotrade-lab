# Small-account research plan

## Objective and success condition

Produce a comparison of two or three fully specified methods for a USD 30 account, including
the possibility that none is feasible. Optimize research for decision value, not source counts
or completion of a universal market-data platform. This is a research plan, not measured results.

User mandate (2026-09-11): approximately USD 30 available, up to 50% loss per method, researcher
chooses evaluation duration and may compare capital/loss/duration scenarios. Keep historical
Gate E1 evidence intact. Its stopped packet must not be rerun or its unused slots reused.

## Fixed scenario grid

| Dimension | Predefined values | Interpretation |
| --- | --- | --- |
| Initial allocation | USD 10, 30, 100, 300 | 30 is the baseline; larger amounts are hypothetical, not a funding request |
| Loss budget | 20%, 35%, 50% of initial allocation | Includes realized/unrealized P&L and fees; no reset or replenishment |
| Evaluation window | 30, 90, 180, 365 calendar days | Report all available windows; missing history stays unavailable |
| Exposure | 0 to 100%, long-only, no borrowing | Each method tested independently |
| Cost stress | verified base costs, 2x variable fees/slippage | Also retain actual fixed fees and order constraints |

Stop generating entries once mark-to-market equity reaches initial capital times (1-loss budget).
Liquidate at the next executable price including costs, then stay in cash to window end. Report
overshoot and inability to liquidate. Peak drawdown is a separate metric, not this stop definition.

## First candidates: researcher-defined baselines

Evaluate a fixed spot instrument and daily bars first to limit data/execution complexity. BTC and
ETH are feasibility candidates, not claims of superior returns. Select one accessible venue using
current official access, fee, minimum-notional, lot/tick, and data-use evidence. No venue is assumed
available. Use USD-equivalent capital only with a dated FX/conversion-cost assumption where needed.
If no spot venue qualifies, record that result before assessing a fixed Korean ETF alternative.

Freeze the following rules before inspecting performance. These are explicit project adaptations,
not claims that a publication specified the exact implementation:

1. Trend breakout: while flat, enter when daily close exceeds the prior 55-bar high; exit when
   close falls below the prior 20-bar low. Ignore short-side breakouts. Warm-up: 55 complete bars.
2. Trend filter: hold when the 20-bar mean close exceeds the 100-bar mean; otherwise cash.
   Warm-up: 100 complete bars; no short exposure.
3. Mean reversion: Wilder RSI(14), initialized with the first 14 gains/losses' arithmetic means,
   then smoothed with alpha 1/14. Enter below 30, exit at or above 50. All-zero gains/losses =>
   RSI 50; zero loss with positive gain => 100. Warm-up: 14 price changes.

Each decision uses only a completed bar; execute at the next available bar open with slippage.
Deploy the maximum affordable rounded quantity after fees, retain residual cash, and never create
negative cash. Use one position at a time. Daily observations can miss intraday threshold breaches;
disclose this and do not claim continuous stop protection. Intraday stops require separate data.
Compare cash and buy-and-hold under identical costs, windows, and order constraints; show both
stopped and unstopped buy-and-hold. Existing signed strategies are not drop-in spot implementations.

## Data gate scoped to the experiment

Before performance testing verify instrument identity/lifecycle for the sampled interval, complete
bars and timestamps, duplicates/gaps, allowed private retention/use, and official trading rules.
A fixed-instrument study is conditional on that instrument and cannot support whole-market claims
or eliminate retrospective asset-selection bias. A whole-market selection strategy still requires
point-in-time membership and delisted coverage. Never relabel an old NO-GO dataset as approved.
Public documentation reads and offline implementation may proceed; credentials, purchases and
new bounded market-data collection follow the applicable repository gate.

## Evaluation and selection

Use at least three chronological years plus warm-up if legitimately available; otherwise explicitly
restrict conclusions. Freeze dates and split 60% development / 20% validation / 20% untouched test.
Do not shuffle. Purge evaluation windows crossing split boundaries. Mark overlapping windows as
dependent; do not count them as independent samples. Publish dates and all attempted variants.

Choose any suggested capital/loss/duration range on development and validation only, then evaluate
once on test. Do not tune again after test. Report the complete grid rather than only its winner.
Favor a stable tradeoff range over a single historical maximum. Neighboring scenarios and doubled
costs should not reverse the conclusion without being highlighted.

Report terminal USD P&L, net return, excess over buy-and-hold, maximum drawdown, loss-stop frequency
across windows, stop overshoot, turnover, fee drag, residual cash, rejected orders and trade count.
Also report observed +25%, +50%, +100% attainment rates and times alongside loss outcomes; these
are historical frequencies, not forecasts. Expose worst windows and capital locked up.

Minimum executable capital is the observed amount needed for order/fee constraints at the tested
prices; it is different from a suggested research allocation and is not a timeless venue minimum.
Do not assert that USD 100/300 is needed for profitability from a single winning run.

For prospective paper evaluation, plan at least 90 days and 30 completed round trips; extend to
180/365 days if sparse. These are scheduling heuristics, not statistical sufficiency guarantees.
At 365 days report insufficient evidence if needed rather than extending indefinitely. Funding
and leverage research are deferred until a distinct plan models their additional costs and risks.

## Delivery sequence

1. SMALL-001: feasibility evidence table for one venue and fixed instruments, dated official
   sources, proposed bounded dataset packet; select no strategy by claimed return.
2. SMALL-002: quantity/cash/order-aware simulator and above rules, with meaningful tests for
   unaffordable orders, rounding, next-open fills, fees, stop overshoot and no re-entry after stop.
3. SMALL-003: approved data verification and frozen full-grid comparison, including negative
   results, followed by a proposed paper-evaluation duration.

Completion is a reproducible comparison artifact, or an explicit feasibility rejection with the
minimum missing evidence. Existing VectorBacktester is insufficient for this experiment: initial
cash currently rescales equity without changing fills or feasibility.
