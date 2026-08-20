"""Validate staging JSONL and emit a deterministic dry-run aggregate report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from autotrade_lab.research.staging import aggregate

ROOT = Path(__file__).parents[1]
DEFAULT_DIR = ROOT / "research" / "staging" / "fixtures" / "luna-101"
DEFAULT_REPORT = ROOT / "research" / "runs" / "LUNA-100-staging-dry-run.json"


def run(staging_dir: Path = DEFAULT_DIR, report_path: Path = DEFAULT_REPORT) -> dict:
    report = aggregate(staging_dir)
    report["staging_dir"] = (
        "research/staging/fixtures/luna-101" if staging_dir == DEFAULT_DIR else str(staging_dir)
    )
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staging-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--apply", action="store_true", help="reserved safety gate; automatic merge is disabled"
    )
    args = parser.parse_args()
    if args.apply:
        parser.error("automatic merge is disabled; review the dry-run report first")
    report = run(args.staging_dir, args.report)
    print(json.dumps(report["counts"], sort_keys=True))
