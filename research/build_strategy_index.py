"""Build the browsing index from canonical strategy JSON records."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from autotrade_lab.research.validation import load_strategy_record

ROOT = Path(__file__).parents[1]
DEFAULT_INPUT = ROOT / "research" / "strategies"
DEFAULT_INDEX = ROOT / "research" / "strategy_index.csv"
FIELDNAMES = [
    "id",
    "canonical_name",
    "family",
    "markets",
    "asset_direction",
    "execution_scope",
    "status",
]


def _records(input_dir: Path) -> list[dict]:
    paths = sorted(input_dir.glob("*.json"))
    if not paths:
        raise ValueError(f"no strategy JSON records found in {input_dir}")
    records = []
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for path in paths:
        if path.stem != path.name.removesuffix(".json"):
            raise ValueError(f"{path}: expected a .json strategy record")
        record = load_strategy_record(path)
        if path.stem != record["id"]:
            raise ValueError(f"{path}: filename stem must match $.id ({record['id']!r})")
        if record["id"] in seen_ids:
            raise ValueError(f"{path}: duplicate $.id {record['id']!r}")
        if record["canonical_name"] in seen_names:
            raise ValueError(f"{path}: duplicate $.canonical_name {record['canonical_name']!r}")
        seen_ids.add(record["id"])
        seen_names.add(record["canonical_name"])
        records.append(record)
    return records


def rows_from_records(records: list[dict]) -> list[dict[str, str]]:
    return [
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


def build_index(input_dir: Path = DEFAULT_INPUT, index_path: Path = DEFAULT_INDEX) -> int:
    records = _records(input_dir)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows_from_records(records))
    return len(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    args = parser.parse_args()
    print(f"indexed {build_index(args.input_dir, args.index)} strategy records")
