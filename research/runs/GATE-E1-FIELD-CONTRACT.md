# Gate E1 official response-field contract

- Prepared: 2026-08-28 KST
- Final review: 2026-09-04 KST
- Scope: Financial Services Commission public-data responses used by the bounded Korean daily-data
  eligibility packet
- Contract SHA-256: `fa60afc780c3dee48fa1e345477758925da1754f3c767f09a0f839e657f024bc`
- Public-data requests made while preparing this contract: 0

The field names below are pinned from the official Public Data Portal Swagger embedded in the four
publication pages. A returned item must contain every field for its operation as a string. The
semantic validator separately requires identity fields to be nonempty, enforces request filters,
checks OHLCV ordering and numeric values, and rejects duplicate identities. Undocumented extra
fields may be retained as provider evidence but cannot satisfy a missing documented field.

| Official publication | Operation | Required item fields |
| --- | --- | --- |
| [KRX listed instruments](https://www.data.go.kr/data/15094775/openapi.do) | `getItemInfo` | `basDt`, `srtnCd`, `isinCd`, `mrktCtg`, `itmsNm`, `crno`, `corpNm` |
| [Stock prices](https://www.data.go.kr/data/15094808/openapi.do) | `getStockPriceInfo` | `basDt`, `srtnCd`, `isinCd`, `itmsNm`, `mrktCtg`, `clpr`, `vs`, `fltRt`, `mkp`, `hipr`, `lopr`, `trqu`, `trPrc`, `lstgStCnt`, `mrktTotAmt` |
| [Stock prices](https://www.data.go.kr/data/15094808/openapi.do) | `getSecuritiesPriceInfo` | `vs`, `fltRt`, `mkp`, `lopr`, `trqu`, `trPrc`, `stLstgCnt`, `mrktTotAmt`, `basDt`, `srtnCd`, `isinCd`, `itmsNm`, `clpr`, `hipr` |
| [Stock issuance](https://www.data.go.kr/data/15043423/openapi.do) | `getItemBasiInfo_V3` | `basDt`, `crno`, `isinCd`, `stckIssuCmpyNm`, `isinCdNm`, `scrsItmsKcd`, `scrsItmsKcdNm`, `stckParPrc`, `issuStckCnt`, `lstgDt`, `lstgAbolDt`, `dpsgRegDt`, `dpsgCanDt`, `issuFrmtClsfNm`, `itmsShrtnCd` |
| [Stock issuance](https://www.data.go.kr/data/15043423/openapi.do) | `getStocIssuInfo_V3` | `basDt`, `crno`, `isinCd`, `isinCdNm`, `stckIssuCmpyNm`, `scrsDcd`, `stckIssuSqno`, `stckIssuDt`, `stckIssuDcnt`, `scrsItmsKcd`, `scrsItmsKcdNm`, `stckIssuRcd`, `stckIssuRcdNm`, `issuStckCnt`, `lstgDt` |
| [Stock dividends](https://www.data.go.kr/data/15043284/openapi.do) | `getDiviInfo_V2` | `basDt`, `crno`, `isinCd`, `isinCdNm`, `stckIssuCmpyNm`, `dvdnBasDt`, `cashDvdnPayDt`, `stckHndvDt`, `stckDvdnRcd`, `stckDvdnRcdNm`, `trsnmDptyDcd`, `trsnmDptyDcdNm`, `scrsItmsKcd`, `scrsItmsKcdNm`, `stckGenrDvdnAmt`, `stckGrdnDvdnAmt`, `stckGenrCashDvdnRt`, `stckGenrDvdnRt`, `cashGrdnDvdnRt`, `stckGrdnDvdnRt`, `stckParPrc`, `stckStacMd` |

The official page and guide fingerprints remain those recorded in
`research/runs/GATE-E1-PREP-EVIDENCE.md`. The documented JSON envelope is top-level `header` and
`body`; the prior bounded diagnostic observed a sole top-level `response` wrapper. Exactly those two
forms are admitted. A mixed form or a wrapper with sibling keys fails closed.
