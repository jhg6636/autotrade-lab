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

## Decisions required before backtesting or paper trading

The user must later set explicit values for:

1. initial experiment capital;
2. maximum total loss in currency and as a fraction of that capital;
3. maximum acceptable drawdown before the system stops;
4. whether any leverage is ever permitted and its absolute cap;
5. minimum evaluation horizon before abandoning or changing a rule.

Until those values are supplied, this profile influences safety and feasibility only. It does not
authorize ranking, backtesting, paper trading, live trading, or an implied return promise.
