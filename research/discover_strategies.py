"""Run a non-mutating strategy discovery/deduplication dry run."""

from __future__ import annotations

import argparse
from pathlib import Path

from autotrade_lab.research.discovery import run_dry_run

ROOT = Path(__file__).parents[1]
DEFAULT_INPUT = ROOT / "research" / "strategies"
DEFAULT_REPORT = ROOT / "research" / "runs" / "LUNA-003-dry-run.json"


def run(input_dir: Path = DEFAULT_INPUT, report_path: Path | None = DEFAULT_REPORT) -> dict:
    return run_dry_run(input_dir, report_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="reserved safety gate; automatic merge is not implemented",
    )
    args = parser.parse_args()
    if args.apply:
        parser.error("automatic merge is disabled; review the dry-run report first")
    report = run(args.input_dir, args.report)
    print(f"dry-run suggestions: {len(report['suggestions'])}; no strategy records changed")
