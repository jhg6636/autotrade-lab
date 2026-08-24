# Gate E1-PREP — Korean daily-data collector packet

- Base commit: `6bf607a`
- Working branch: `agent/GATE-E1-PREP`
- Prepared: 2026-08-24 KST
- Stage: complete; E1-DATA not authorized

## Objective and boundary

E1-PREP pins the official documentation, rights classification, exact 24-request table, and a
fail-closed collector for a small Korean daily-data feasibility probe. It performs no API data
request and creates no service key. It does not backtest, rank, optimize, access a brokerage
account, place an order, or trade.

E1-DATA remains a separate gate. The collector rejects execution unless its exact plan SHA-256 is
passed back after user review.

## Documentation result

The four admitted Public Data Portal publications have been reduced to six exact HTTPS operations:

1. `/service/GetKrxListedInfoService/getItemInfo`;
2. `/service/GetStockSecuritiesInfoService/getStockPriceInfo`;
3. `/service/GetStockSecuritiesInfoService/getSecuritiesPriceInfo`;
4. `/GetStocIssuInfoService_V3/getItemBasiInfo_V3`;
5. `/GetStocIssuInfoService_V3/getStocIssuInfo_V3`;
6. `/GetStocDiviInfoService_V2/getDiviInfo_V2`.

Source-page, guide, policy, fixed-sample hashes, rights reasoning, and the V3 parameter conflict are
recorded in `research/runs/GATE-E1-PREP-EVIDENCE.md`.

## Collector contract

`src/autotrade_lab/gate_e1_prep.py`:

- defines exactly 24 immutable slots and plan SHA-256
  `ae802b8d4245a153af5abea3e2875049ee086e6556541ff3f8f1a5d2677198f0`;
- includes every base URL, operation, page, filter, and per-slot budget in that hash;
- fixes `numOfRows=50`, JSON output, exact page numbers, filters, and 218,000 response bytes per slot;
- permits only the six operations above on `https://apis.data.go.kr`;
- permits page 2 only for the named listed-instrument and stock-price pagination slots;
- requires a mode-`0600`, regular non-symlink file containing only
  `PUBLIC_DATA_SERVICE_KEY_DECODED=...`;
- injects the key only into the live request, never the safe plan, manifest, raw filename, header,
  log, or raised stop message;
- rejects decoded and URL-encoded key echoes before retaining a body;
- rejects redirects, non-JSON, non-200, invalid provider result code/schema, mismatched paging,
  more than 50 rows, invalid/oversized `Content-Length`, streaming overflow, or cumulative overflow;
- performs no retry and has no executable CLI;
- writes raw bodies only after key/schema/row/byte checks and writes a canonical manifest only after
  all 24 slots succeed;
- provides `verify_gate_e1_data()` to recompute every raw checksum, byte count, row count, exact raw
  file set, request metadata/outcome/order, plan/limits, safe headers, and cumulative total without a
  credential.

The Git-ignored key file is not created during E1-PREP. `.gitignore` already excludes `.env.*`.

## Exact E1-DATA request table — not authorized

All slots use JSON, `numOfRows=50`, page 1 unless shown, at most 218,000 bytes, and one attempt.
`20260821` is the fixed last completed publication date selected during preparation; it is not
advanced automatically if execution occurs later.

| # | Request ID | Operation | Fixed filters |
| ---: | --- | --- | --- |
| 1 | `listing_2009_boundary` | `getItemInfo` | `basDt=20091231` |
| 2 | `listing_2010_boundary` | `getItemInfo` | `basDt=20100104` |
| 3 | `listing_probe_page_1` | `getItemInfo` | `basDt=20260821` |
| 4 | `listing_probe_page_2` | `getItemInfo`, page 2 | `basDt=20260821` |
| 5 | `listing_kosdaq_sentinel` | `getItemInfo` | `basDt=20260821`, `likeSrtnCd=196170` |
| 6 | `listing_etf_sentinel` | `getItemInfo` | `basDt=20260821`, `isinCd=KR7069500007` |
| 7 | `stock_price_2009_boundary` | `getStockPriceInfo` | `basDt=20091231` |
| 8 | `stock_price_2010_boundary` | `getStockPriceInfo` | `basDt=20100104` |
| 9 | `stock_price_probe_page_1` | `getStockPriceInfo` | `basDt=20260821` |
| 10 | `stock_price_probe_page_2` | `getStockPriceInfo`, page 2 | `basDt=20260821` |
| 11 | `stock_price_samsung_pre_split` | `getStockPriceInfo` | `basDt=20180427`, `isinCd=KR7005930003` |
| 12 | `stock_price_samsung_post_split` | `getStockPriceInfo` | `basDt=20180504`, `isinCd=KR7005930003` |
| 13 | `stock_price_hanjin_last_trading_day` | `getStockPriceInfo` | `basDt=20170306`, `likeSrtnCd=117930` |
| 14 | `etf_price_2010_boundary` | `getSecuritiesPriceInfo` | `basDt=20100104`, `isinCd=KR7069500007` |
| 15 | `etf_price_probe_date` | `getSecuritiesPriceInfo` | `basDt=20260821`, `isinCd=KR7069500007` |
| 16 | `issuance_basic_probe_page` | `getItemBasiInfo_V3` | `basDt=20260821` |
| 17 | `issuance_basic_2010_boundary` | `getItemBasiInfo_V3` | `basDt=20100104` |
| 18 | `issuance_basic_samsung_pre_split` | `getItemBasiInfo_V3` | `basDt=20180427`, `crno=1301110006246` |
| 19 | `issuance_basic_samsung_post_split` | `getItemBasiInfo_V3` | `basDt=20180504`, `crno=1301110006246` |
| 20 | `issuance_basic_hanjin_delist` | `getItemBasiInfo_V3` | `basDt=20170307`, `stckIssuCmpyNm=(주)한진해운` |
| 21 | `issuance_history_samsung_post_split` | `getStocIssuInfo_V3` | `basDt=20180504`, `crno=1301110006246` |
| 22 | `dividend_samsung_history` | `getDiviInfo_V2` | `crno=1301110006246` |
| 23 | `dividend_2010_boundary` | `getDiviInfo_V2` | `basDt=20100104` |
| 24 | `dividend_probe_date` | `getDiviInfo_V2` | `basDt=20260821` |

Allocation is listed instruments 6, stock prices 7, investment-security prices 2, issuance 6, and
dividends 3: 24 requests, at most 1,200 rows, and 5,232,000 declared response bytes under the
5,242,880-byte cumulative hard limit.

## Post-call observations and fail-closed decisions

The subsequent E1-DATA report must keep every returned/absent fact as an observation:

- 2009-12-31 and 2010-01-04 presence or absence for listing and stock-price services;
- stable pagination metadata and no cross-page duplicate identity on the two page-2 pairs;
- explicit KOSDAQ identity for `196170` and explicit investment-security identity for KODEX 200;
- Samsung pre/post-split raw OHLCV behavior and whether issuance fields explain the discontinuity;
- Hanjin Shipping short code, ISIN returned by both sources, last-trading price, and exact
  `lstgAbolDt=20170307` without name-based joining or replacement;
- dividend record/payment dates and share-class identity joined through returned identifiers;
- zero-volume/suspended-day and correction semantics only if observed, never inferred;
- safe quota headers and exact no-retry errors.

An empty 2009 result is a valid observation, not a transport failure. A provider error, schema
mismatch, silent latest-date substitution, incorrect identity/date, duplicate pagination, missing
fixed delisted sample, absent explicit ETF identity, key/redirect/budget issue, or disputed V3
parameter requirement stops the run and leaves the affected track `failed` or `limited`. No slot is
replaced and unused budget is not reused.

## Completion and current decision

E1-PREP passed 14 focused tests and 131 full repository tests, Ruff check/format, `git diff --check`,
credential-pattern scan, canonical strategy/index isolation, and final adversarial review. The
review found and resolved three pre-completion defects: the base URL was added to the approval hash,
URL-encoded key material in selected headers is rejected before manifest retention, and the local
verifier now rejects request-metadata/limit/outcome changes and extra raw files. No P1/P2 remains.
Completion authorizes only a user review of this exact plan hash.

E1-DATA remains **closed**. It requires a separate explicit approval, a user-created Public Data
Portal key supplied locally through the private ignored file, and no documentation or license
change. E1-DATA still does not authorize backtesting or trading.
