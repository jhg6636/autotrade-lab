# Gate E0 official-source evidence log

- Retrieval completed: 2026-08-24T16:51:12+09:00
- Method: public official pages only; no login, key creation, terms acceptance, API data request,
  purchase, or download
- Purpose: record exact official page fields used in `GATE-E0.md`; mutable pages are not treated as
  immutable snapshots

## KRX Open API

- [Service list](https://openapi.krx.co.kr/contents/OPP/INFO/service/OPPINFO004.cmd): page states a
  2010+ target period; KOSPI/KOSDAQ stock daily, stock basic information, and ETF daily trading each
  state 2010-01-04 as the first offered date.
- [Terms](https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO002.jsp), effective 2025-12-26:
  - Article 6(2): noncommercial purpose only; no charging third parties for API results.
  - Article 8(4): one key, at most 10,000 requests per calendar day.
  - Article 10(3): a screen using results must identify KRX statistical information.
  - Article 11(2): received information may not be provided to a third party.
  - Article 11(3): received information may not be used after the use contract ends.
  - Article 12(2,5): accuracy/completeness and continued provision are not guaranteed.

## Financial Services Commission publications on the Public Data Portal

- [KRX listed-instrument API](https://www.data.go.kr/data/15094775/openapi.do):
  - base `apis.data.go.kr/1160100/service/GetKrxListedInfoService`;
  - operation `/getItemInfo`;
  - paging parameters `numOfRows`, `pageNo`; exact-date parameter `basDt`; identity filters include
    `likeSrtnCd`, `isinCd`, and `crno`;
  - result fields `basDt`, `srtnCd`, `isinCd`, `mrktCtg`, `itmsNm`, `crno`, `corpNm`;
  - free, automatic approval, development traffic 10,000, displayed license unrestricted, published
    time range blank.
- [Stock-price API](https://www.data.go.kr/data/15094808/openapi.do):
  - base `apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService`;
  - `/getStockPriceInfo` for stock and `/getSecuritiesPriceInfo` for investment securities;
  - paging and exact/range date plus code/ISIN filters are exposed;
  - stock result model includes date, short code, ISIN, market, open, high, low, close, volume, value,
    listed shares, and market capitalization;
  - free, automatic approval, development traffic 10,000, displayed license unrestricted, published
    time range blank; the page also says the provider batch updates once per business day.
- [Stock-issuance API](https://www.data.go.kr/data/15043423/openapi.do): four operations are described;
  basic issue fields include listing/delisting dates, while issue history includes issue date/round/
  reason. Public Nuri Type 2, free, development traffic 10,000, time range blank. Exact Swagger
  operations were not available in the reviewed rendered page and must be resolved in E1-PREP. The
  same official page states that commercial use requires an information-use agreement with KSD.
- [Stock-dividend API](https://www.data.go.kr/data/15043284/openapi.do): record date, cash payment date,
  stock delivery date, amount/rate, share type, and reason are described. Public Nuri Type 2, free,
  development traffic 10,000, time range blank. The page states that commercial use requires a KSD
  information-use agreement. Exact operation must be resolved in E1-PREP.
- [Portal use policy](https://www.data.go.kr/ugs/selectPortalPolicyView.do): third-party rights must be
  reflected in the displayed license. Public Nuri Type 2 requires attribution, permits only
  noncommercial use, and permits derivative works.

## OpenDART

- [Introduction](https://opendart.fss.or.kr/intro/main.do): anyone may use the service and may
  download disclosure XML and extract/use desired material.
- [Terms](https://opendart.fss.or.kr/intro/terms.do): service is free in principle, API/program
  copyright belongs to FSS, unspecified copyright matters follow copyright/public-data law, key
  sharing is prohibited, and disclosure accuracy/completeness is not guaranteed.
- [Bonus-issue guide](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS005&apiId=2020024):
  `/api/fricDecsn`, 2015+; fields include record date, shares allocated per existing share, dividend
  accrual date, planned listing date, and board-decision date. Other documented major-report guides
  cover selected capital reduction, merger, and company-division events, not a complete price-factor
  feed.

## Review boundary

The evidence above documents fields, displayed licenses, and service claims. It does not establish
actual historical depth, point-in-time completeness, ETF lifecycle coverage, durable storage rights,
correction behavior, or adjusted-price methodology. Those remain conditional or unknown.
