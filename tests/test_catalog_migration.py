import csv
import importlib
import importlib.util
import json
from pathlib import Path

from autotrade_lab.catalog import CATALOG
from autotrade_lab.research.validation import load_strategy_record

_MODULE_PATH = Path(__file__).parents[1] / "research" / "migrate_catalog.py"
_SPEC = importlib.util.spec_from_file_location("catalog_migration", _MODULE_PATH)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
generate = _MODULE.generate


def test_catalog_migration_is_complete_and_valid(tmp_path):
    output = tmp_path / "strategies"
    index = tmp_path / "strategy_index.csv"
    assert generate(output, index) == len(CATALOG)
    records = list(output.glob("*.json"))
    assert len(records) == len(CATALOG)
    for path in records:
        load_strategy_record(path)
    with index.open(newline="", encoding="utf-8") as handle:
        assert len(list(csv.DictReader(handle))) == len(CATALOG)


def test_catalog_migration_is_deterministic(tmp_path):
    output = tmp_path / "strategies"
    index = tmp_path / "strategy_index.csv"
    generate(output, index, force=True)
    first = {path.name: path.read_text(encoding="utf-8") for path in output.glob("*.json")}
    first_index = index.read_text(encoding="utf-8")
    generate(output, index, force=True)
    assert first == {path.name: path.read_text(encoding="utf-8") for path in output.glob("*.json")}
    assert first_index == index.read_text(encoding="utf-8")


def test_migration_does_not_create_evidence_or_priority_fields(tmp_path):
    output = tmp_path / "strategies"
    generate(output, tmp_path / "index.csv")
    forbidden = {"evidence", "confidence", "priority", "rank", "score", "popularity"}
    for path in output.glob("*.json"):
        assert not forbidden.intersection(json.loads(path.read_text(encoding="utf-8")))


def test_implemented_entries_link_to_code(tmp_path):
    output = tmp_path / "strategies"
    generate(output, tmp_path / "index.csv")
    implemented = [spec.key for spec in CATALOG if spec.status == "implemented"]
    for key in implemented:
        record = json.loads((output / f"{key}.json").read_text(encoding="utf-8"))
        implementation = record["implementation"]
        path = Path(__file__).parents[1] / implementation["path"]
        assert path.is_file()
        module_name = (
            implementation["path"].removeprefix("src/").removesuffix(".py").replace("/", ".")
        )
        assert hasattr(importlib.import_module(module_name), implementation["symbol"])


def test_migration_refuses_to_overwrite_canonical_records(tmp_path):
    import pytest

    output = tmp_path / "strategies"
    generate(output, tmp_path / "index.csv")
    with pytest.raises(FileExistsError, match="canonical strategy records"):
        generate(output, tmp_path / "index.csv")
