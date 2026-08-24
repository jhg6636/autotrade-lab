# Gate C public crypto sample — local artifact index

The user approved this bounded capability sample on 2026-08-24. The collector attempted the 12
allowlisted public requests exactly once and did not use credentials or private/order endpoints.

Raw response bodies and normalized Parquet are retained locally but excluded from Git pending an
explicit provider-terms and redistribution decision. This repository commits the request manifest,
quality report, checksums, collector, and verification tests without publishing market-value rows.

## Local artifacts

| Artifact | Bytes | SHA-256 | Git policy |
| --- | ---: | --- | --- |
| `manifest.json` | 12,860 | `7ae502ba69a0305a72fa88d4c4e5d2572ed55c7032ac9ba5a116b204517dbbc7` | tracked |
| `quality_report.json` | 7,080 | `0795f478faef213d377c6d123c7a3e045cc21a6895bfa835982686e515bde330` | tracked |
| `normalized/candles.parquet` | 312,978 | `9a9d59f2dce69edce8d840309b079bb5b546dc665635b6d456ec0c6c4489fe10` | local, ignored |
| 12 files under `raw/` | 1,628,753 total | per-response hashes in `manifest.json` | local, ignored |

The full local run is 1,963,244 bytes, below the 25 MB Gate C bound. `verify-crypto` regenerates the
Parquet and quality report from raw files and requires byte identity.

```bash
.venv/bin/python -m autotrade_lab.data_probe verify-crypto \
  research/probes/gate-c-public-crypto-20260824
```

Do not re-run `collect-crypto` to replace missing local raw files: that would be a new market-data
sample, not reproduction of this run, and requires a new request budget and user decision.
