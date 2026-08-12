"""Generate schema records from the initial Python strategy catalog.

This is deliberately conservative: the initial catalog contains hypotheses and family-level
metadata, not source-backed entry/exit formulas. Unknown rules are recorded explicitly instead
of being invented. Running the command twice is deterministic.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from autotrade_lab.catalog import CATALOG
from autotrade_lab.research.validation import validate_strategy_record

ROOT = Path(__file__).parents[1]
DEFAULT_OUTPUT = ROOT / "research" / "strategies"
DEFAULT_INDEX = ROOT / "research" / "strategy_index.csv"
IMPLEMENTATIONS = {
    "buy_hold": ("src/autotrade_lab/strategies.py", "BuyAndHold"),
    "ma_cross": ("src/autotrade_lab/strategies.py", "MovingAverageCross"),
    "donchian": ("src/autotrade_lab/strategies.py", "DonchianBreakout"),
    "ts_momentum": ("src/autotrade_lab/strategies.py", "TimeSeriesMomentum"),
    "cross_sectional_momentum": (
        "src/autotrade_lab/portfolio_strategies.py",
        "CrossSectionalMomentum",
    ),
    "dual_momentum": ("src/autotrade_lab/portfolio_strategies.py", "DualMomentum"),
    "rsi_reversion": ("src/autotrade_lab/strategies.py", "RsiMeanReversion"),
    "bollinger_reversion": ("src/autotrade_lab/strategies.py", "BollingerMeanReversion"),
    "overnight_gap_fade": ("src/autotrade_lab/strategies.py", "GapFade"),
    "pairs_distance": ("src/autotrade_lab/portfolio_strategies.py", "pairs_zscore"),
    "volatility_breakout": ("src/autotrade_lab/strategies.py", "VolatilityBreakout"),
    "volume_momentum": ("src/autotrade_lab/strategies.py", "VolumeMomentum"),
    "funding_carry": ("src/autotrade_lab/portfolio_strategies.py", "funding_carry_weights"),
    "risk_parity": ("src/autotrade_lab/portfolio_strategies.py", "InverseVolatility"),
    "volatility_target": ("src/autotrade_lab/portfolio_strategies.py", "InverseVolatility"),
}


def _markets(values: tuple[str, ...]) -> list[str]:
    mapped = []
    for value in values:
        mapped.extend(
            {"crypto": ["crypto_spot", "crypto_perp"], "all": ["multi_asset"]}.get(value, [value])
        )
    return list(dict.fromkeys(mapped))


def _direction(markets: list[str]) -> str:
    if set(markets) & {"kr_equity", "kr_etf"}:
        return "long_only"
    if set(markets) & {"crypto_spot", "crypto_perp"}:
        return "long_short"
    return "directionless"


def _record(spec):
    markets = _markets(spec.markets)
    status = "hypothesis" if spec.status == "research_only" else spec.status
    record = {
        "id": spec.key,
        "canonical_name": spec.key.replace("_", " ").title(),
        "aliases": [],
        "family": spec.family,
        "markets": markets,
        "asset_direction": _direction(markets),
        "execution_scope": "context_only" if spec.status == "research_only" else "executable",
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
        }
    return validate_strategy_record(record)


def generate(output_dir: Path = DEFAULT_OUTPUT, index_path: Path = DEFAULT_INDEX) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    records = [_record(spec) for spec in CATALOG]
    for record in records:
        (output_dir / f"{record['id']}.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    rows = [
        {
            "id": record["id"],
            "canonical_name": record["canonical_name"],
            "family": record["family"],
            "markets": ";".join(record["markets"]),
            "asset_direction": record["asset_direction"],
            "execution_scope": record["execution_scope"],
            "status": record["status"],
        }
        for record in records
    ]
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    args = parser.parse_args()
    print(f"generated {generate(args.output_dir, args.index)} strategy records")
