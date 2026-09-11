# Investor profile — segregated high-upside experiment

## Persona

The intended user can allocate only a small amount to automated trading and wants substantial
percentage upside. This is an **experimental risk-capital account**, not an income, emergency-fund,
retirement, or capital-preservation account.

Automation does not create an edge or make a high return probable. A high target return normally
requires accepting higher volatility, concentration, leverage, or tail risk. The project therefore
interprets the objective as: seek asymmetric upside only after bounding the amount that can be lost.

## Design implications

- Capital is segregated from living expenses and long-term savings.
- The system never pulls additional money automatically. Deposits require a new user decision.
- Martingale, loss-chasing, and position increases triggered only by prior losses are forbidden.
- Borrowing and leverage remain disabled until a later evidence gate explicitly evaluates them.
- A desired return is not a pre-data rank, optimization target, or reason to select a source.
- Small-account evaluation must include minimum order size, tick/lot rounding, fixed fees, spread,
  turnover, idle cash, and the possibility that a theoretically valid allocation is untradeable.
- Survival metrics precede return metrics: capital-at-risk, probability of ruin, peak-to-trough
  drawdown, tail loss, liquidation distance, venue failure, and kill-switch behavior.
- No strategy may silently assume that the user will replenish losses.

## User-confirmed research baseline — 2026-09-11

The user has approximately USD 30 available and accepts a loss of up to 50% per method.
Interpret USD 30 as the total available experimental capital, not USD 30 per concurrent method.
Each independent simulation may start with USD 30; these are alternative worlds, not simultaneous
funded accounts. A method allocated USD 10 has a USD 5 baseline loss budget; full allocation has
a USD 15 budget. No automatic replenishment or reset after a stop is allowed.

The user delegated evaluation-period selection and approved research scenarios for capital, loss
budget, and duration. These inputs are no longer blockers to offline research. Use
`SMALL_ACCOUNT_RESEARCH.md` for the predefined comparison grid and validation conditions.
Loss budget is measured from initial allocated capital, separately from peak drawdown. A threshold
triggers an exit at the next executable price and is not a guaranteed realized-loss ceiling.

## Decisions still required before funded deployment

Before funded deployment, confirm:

1. initial experiment capital;
2. maximum total loss in currency and as a fraction of that capital;
3. maximum acceptable drawdown before the system stops;
4. whether any leverage is ever permitted and its absolute cap;
5. minimum evaluation horizon before abandoning or changing a rule.

Research scenarios do not authorize funded deployment. Aggregate account loss across concurrent
or sequential methods remains a separate deployment decision. Initial research uses unlevered,
long-only exposure; acceptable loss does not imply permission to borrow or use leverage.
