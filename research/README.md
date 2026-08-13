# Strategy research data

The JSON files in `strategies/` are the canonical strategy records. Edit and review those files
directly. `strategy_index.csv` is a derived browsing artifact and must not be treated as evidence.

`migrate_catalog.py` is a one-time bootstrap from the legacy Python `CATALOG`. It refuses to
overwrite existing JSON unless `--force` is explicitly supplied, because later research can add
source-backed detail that the legacy catalog cannot reproduce.

An `implementation` link describes its actual coverage: a full target generator, portfolio
weights, a signal only, or one leg of a larger trade. It does not mean the strategy is ready for
live trading. Korean equity and ETF applications are always executable as long-only; constraints
for mixed-market records are represented separately in `applications`.
