# Strategy research catalog

The executable registry is `autotrade_lab.catalog.CATALOG`. A row marked **implemented**
means only that a reproducible baseline signal exists. It does not mean the strategy is
profitable. Every candidate must pass walk-forward and paper-trading gates after fees,
slippage, taxes, funding, borrow, latency, and failed fills.

## Families covered

| Family | Candidate methods | Primary use |
|---|---|---|
| Trend | moving averages, Donchian, time-series momentum | liquid ETFs and crypto |
| Cross-sectional momentum | winner-minus-loser, dual momentum | equity/ETF universes |
| Mean reversion | RSI, Bollinger z-score, gap fade | liquid instruments |
| Statistical arbitrage | distance pairs, cointegration, PCA residual | baskets and close substitutes |
| Breakout | range/volatility breakout, opening range | intraday and daily |
| Microstructure | VWAP reversion, volume confirmation, order-book imbalance | high-quality tick data |
| Events | listings, earnings drift, index rebalance | point-in-time event data |
| Carry/basis | spot-perp funding, cash-and-carry, cross-venue funding | crypto derivatives |
| Arbitrage | triangular and cross-venue spread, KRW premium monitor | pre-funded venues only |
| Equity factors | value, quality, low volatility, size | KRX point-in-time fundamentals |
| Allocation | risk parity, volatility targeting | ETF/asset portfolios |
| Ensembles | trend/reversion mix, regime switching | portfolio layer |
| Machine learning | return ranking, execution policy | research-only until strict OOS proof |

## Evidence and cautions

- Time-series and cross-sectional momentum have broad historical evidence, but momentum
  suffers severe crash states and implementation costs matter.
- Pairs trading is a temporary-mispricing hypothesis. Pair formation and delisting must be
  point-in-time to avoid survivorship and look-ahead bias.
- Volatility scaling is economically intuitive, yet published out-of-sample critiques show
  that historical gains are not universal. It is a risk overlay, not guaranteed alpha.
- Perpetual funding is compensation for basis and venue risk, not free yield. Both legs,
  collateral, liquidation, caps, and funding timing must be simulated.
- Short-horizon OHLCV/ML signals often disappear after costs. Failed experiments remain in
  the registry to prevent repeated data mining.

## Promotion gate

1. Freeze hypothesis and parameters before evaluating the holdout.
2. Use point-in-time constituents, corporate actions, announcements, and fundamentals.
3. Model all cash flows and conservative market impact.
4. Run anchored and rolling walk-forward tests across bull, bear, and sideways regimes.
5. Correct for multiple trials; report all attempted variants, not only the winner.
6. Shadow real-time decisions, then paper trade through live broker data.
7. Permit tiny live capital only after operational reconciliation tests pass.
8. Increase capital by risk budget, never because of a short winning streak.

## Key references

- Moskowitz, Ooi, Pedersen, *Time Series Momentum*; Hurst, Ooi, Pedersen,
  *A Century of Evidence on Trend-Following Investing*.
- Chan, Jegadeesh, Lakonishok, *Momentum Strategies*.
- Gatev, Goetzmann, Rouwenhorst, *Pairs Trading: Performance of a Relative-Value
  Arbitrage Rule*.
- Moreira and Muir, *Volatility Managed Portfolios*, together with Cederburg et al.'s
  out-of-sample critique.
- He, Manela, Ross, von Wachter, *Fundamentals of Perpetual Futures*.
- Dobrynskaya, *Cryptocurrency Momentum and Reversal*.

See `docs/SOURCES.md` for direct links and API documentation.
