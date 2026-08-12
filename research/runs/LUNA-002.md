# LUNA-002 run report

- Starting commit: `2b3840b75ca2e6be82bb21ce0110c733b26eecc0` (merged LUNA-001)
- Finished implementation commit: `ae79b68b80f5d13f6f246c4ca983158d181f0194`
- Started/finished at (KST): 2026-08-12 / 2026-08-12
- Inputs inspected: `src/autotrade_lab/catalog.py`, LUNA-001 schema and validator, `docs/RESEARCH_PROTOCOL.md`
- Sources added: none; each migrated record points to the initial local catalog provenance
- Files changed: 35 JSON strategy records, deterministic CSV index, migration generator, migration tests
- Commands run: `.venv/bin/python research/migrate_catalog.py`; `.venv/bin/pytest -q`; `.venv/bin/ruff format .`; `.venv/bin/ruff check .`; `git diff --check`
- Test results: 26 passed; Ruff clean; diff check clean
- Assumptions: `crypto` maps to both `crypto_spot` and `crypto_perp`; `all` maps to `multi_asset`; unimplemented rules remain explicit unknowns
- Ambiguities preserved: initial catalog family hypotheses do not define exact entry, exit, sizing, timeframe, or required fields
- Blockers: none
- Recommended next task: LUNA-003 duplicate/variant/related-to mechanics after review
