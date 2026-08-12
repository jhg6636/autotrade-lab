"""Generate schema records from the initial Python strategy catalog.

This is deliberately conservative: the initial catalog contains hypotheses and family-level
metadata, not source-backed entry/exit formulas. Unknown rules are recorded explicitly instead
of being invented. This is a one-time bootstrap tool; JSON records become canonical.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autotrade_lab.catalog import CATALOG
from autotrade_lab.research.validation import validate_strategy_record
from research.build_strategy_index import build_index

ROOT = Path(__file__).parents[1]
DEFAULT_OUTPUT = ROOT / "research" / "strategies"
DEFAULT_INDEX = ROOT / "research" / "strategy_index.csv"
IMPLEMENTATIONS = {
    "buy_hold": (
        "src/autotrade_lab/strategies.py",
        "BuyAndHold",
        "strategy_target",
        "Complete baseline target generator.",
    ),
    "ma_cross": (
        "src/autotrade_lab/strategies.py",
        "MovingAverageCross",
        "strategy_target",
        "Complete baseline target generator.",
    ),
    "donchian": (
        "src/autotrade_lab/strategies.py",
        "DonchianBreakout",
        "strategy_target",
        "Complete baseline target generator.",
    ),
    "ts_momentum": (
        "src/autotrade_lab/strategies.py",
        "TimeSeriesMomentum",
        "strategy_target",
        "Complete baseline target generator.",
    ),
    "cross_sectional_momentum": (
        "src/autotrade_lab/portfolio_strategies.py",
        "CrossSectionalMomentum",
        "portfolio_weights",
        "Weight generator; execution and portfolio accounting remain external.",
    ),
    "dual_momentum": (
        "src/autotrade_lab/portfolio_strategies.py",
        "DualMomentum",
        "portfolio_weights",
        "Weight generator; execution remains external.",
    ),
    "rsi_reversion": (
        "src/autotrade_lab/strategies.py",
        "RsiMeanReversion",
        "strategy_target",
        "Complete baseline target generator.",
    ),
    "bollinger_reversion": (
        "src/autotrade_lab/strategies.py",
        "BollingerMeanReversion",
        "strategy_target",
        "Complete baseline target generator.",
    ),
    "overnight_gap_fade": (
        "src/autotrade_lab/strategies.py",
        "GapFade",
        "strategy_target",
        "Complete baseline target generator.",
    ),
    "pairs_distance": (
        "src/autotrade_lab/portfolio_strategies.py",
        "pairs_zscore",
        "signal_only",
        "Produces a spread z-score, not tradable pair weights.",
    ),
    "volatility_breakout": (
        "src/autotrade_lab/strategies.py",
        "VolatilityBreakout",
        "strategy_target",
        "Complete baseline target generator.",
    ),
    "volume_momentum": (
        "src/autotrade_lab/strategies.py",
        "VolumeMomentum",
        "strategy_target",
        "Complete baseline target generator.",
    ),
    "funding_carry": (
        "src/autotrade_lab/portfolio_strategies.py",
        "funding_carry_weights",
        "partial_leg",
        "Perpetual leg only; no offsetting spot leg or venue execution.",
    ),
    "risk_parity": (
        "src/autotrade_lab/portfolio_strategies.py",
        "InverseVolatility",
        "portfolio_weights",
        "Inverse-volatility approximation; not covariance-aware risk parity.",
    ),
    "volatility_target": (
        "src/autotrade_lab/portfolio_strategies.py",
        "InverseVolatility",
        "portfolio_weights",
        "Optional volatility cap embedded in inverse-volatility weights.",
    ),
}


def _markets(values: tuple[str, ...]) -> list[str]:
    mapped = []
    for value in values:
        mapped.extend(
            {"crypto": ["crypto_spot", "crypto_perp"], "all": ["multi_asset"]}.get(value, [value])
        )
    return list(dict.fromkeys(mapped))


def _direction(markets: list[str]) -> str:
    if set(markets) & {"kr_equity", "kr_etf"} and set(markets) & {"crypto_spot", "crypto_perp"}:
        return "mixed"
    if set(markets) & {"kr_equity", "kr_etf"}:
        return "long_only"
    if set(markets) & {"crypto_spot", "crypto_perp"}:
        return "long_short"
    return "directionless"


def _applications(markets: list[str], context_only: bool) -> list[dict]:
    applications = []
    for market in markets:
        if market in {"kr_equity", "kr_etf"}:
            direction, exposure = "long_only", {"minimum": 0, "maximum": 1}
        elif market in {"crypto_spot", "crypto_perp"}:
            direction, exposure = "long_short", {"minimum": -1, "maximum": 1}
        else:
            direction, exposure = "directionless", {"minimum": 0, "maximum": 1}
        applications.append(
            {
                "market": market,
                "asset_direction": direction,
                "execution_scope": "context_only" if context_only else "executable",
                "target_exposure": exposure,
            }
        )
    return applications


def _record(spec):
    markets = _markets(spec.markets)
    status = "hypothesis" if spec.status == "research_only" else spec.status
    context_only = spec.status == "research_only"
    record = {
        "id": spec.key,
        "canonical_name": spec.key.replace("_", " ").title(),
        "aliases": [],
        "family": spec.family,
        "markets": markets,
        "asset_direction": _direction(markets),
        "execution_scope": "context_only" if spec.status == "research_only" else "executable",
        "applications": _applications(markets, context_only),
        "timeframes": ["unknown"],
        "sources": [
            {
                "source_type": "original_observation",
                "title": "Initial autotrade-lab strategy catalog",
                "author_or_handle": "autotrade-lab",
                "url": f"local://catalog/{spec.key}",
                "published_at": None,
                "accessed_at": "2026-08-12",
                "language": "en",
                "claim_summary": spec.hypothesis,
                "verbatim_excerpt": None,
            }
        ],
        "hypothesis": spec.hypothesis,
        "entry_rule": "unknown: recover and register an exact rule before backtesting",
        "exit_rule": "unknown: recover and register an exact rule before backtesting",
        "sizing_rule": "unknown: define exposure, leverage, and portfolio limits before backtesting",
        "required_data": ["unknown: determine in LUNA-202 data audit"],
        "execution_assumptions": [
            "no live order",
            "fees and slippage must be specified before evaluation",
        ],
        "variants": [],
        "ambiguities": [
            "Initial catalog records family-level hypotheses only.",
            *spec.main_risks,
        ],
        "status": status,
    }
    if spec.status == "implemented" and spec.key in IMPLEMENTATIONS:
        record["implementation"] = {
            "path": IMPLEMENTATIONS[spec.key][0],
            "symbol": IMPLEMENTATIONS[spec.key][1],
            "coverage": IMPLEMENTATIONS[spec.key][2],
            "notes": IMPLEMENTATIONS[spec.key][3],
        }
    return validate_strategy_record(record)


def generate(
    output_dir: Path = DEFAULT_OUTPUT, index_path: Path = DEFAULT_INDEX, *, force: bool = False
) -> int:
    existing = list(output_dir.glob("*.json")) if output_dir.exists() else []
    if existing and not force:
        raise FileExistsError(
            f"refusing to overwrite {len(existing)} canonical strategy records; pass force=True"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    records = [_record(spec) for spec in CATALOG]
    for record in records:
        (output_dir / f"{record['id']}.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    build_index(output_dir, index_path)
    return len(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--force", action="store_true", help="overwrite existing bootstrap records")
    args = parser.parse_args()
    print(f"generated {generate(args.output_dir, args.index, force=args.force)} strategy records")
