# Gate E1-PREP official documentation evidence

- Retrieval completed: 2026-08-24 KST
- Method: public official documentation pages and their public DOCX guides only
- Excluded: login, utilization application, service-key creation, API data request, account access,
  backtest, order, and trade
- Storage: downloaded documentation was inspected in a temporary directory and is not tracked or
  redistributed; only its SHA-256 and source-stated facts are retained here

## Public Data Portal publications

| Publication | Official page SHA-256 | Official guide SHA-256 | Pinned service and operation |
| --- | --- | --- | --- |
| [KRX listed instruments](https://www.data.go.kr/data/15094775/openapi.do) | `de6c3c9ad3c61cd9619dda344a28044e088f4dcda6ce410919e85ae7d1265b5d` | `f5c34871d834daea234cfdb4d8975ff934d057cd79a3496ab47219f01869bb09` | `https://apis.data.go.kr/1160100/service/GetKrxListedInfoService/getItemInfo` |
| [Stock prices](https://www.data.go.kr/data/15094808/openapi.do) | `779ca314214e44a17b4d59f3bbcbd77d6471c781dcc923761dbd0dcda0ed7f11` | `5d9b2259b37e1bf92bdbb3f3bd76b0ec9d499fb43758a67aa9bf62d2d4a256f4` | `.../GetStockSecuritiesInfoService/getStockPriceInfo`; `.../getSecuritiesPriceInfo` |
| [Stock issuance](https://www.data.go.kr/data/15043423/openapi.do) | `e35561455b704f2d588f7c704ac19bd597d260d88e9915d1faefaf11fa937a8a` | `cddc6e38241bf55705395ba0fa70c10b8c24de3439a84829d3fb297e8aaff5f4` | `https://apis.data.go.kr/1160100/GetStocIssuInfoService_V3/getItemBasiInfo_V3`; `.../getStocIssuInfo_V3` |
| [Stock dividends](https://www.data.go.kr/data/15043284/openapi.do) | `d4e44b8db7a390d9da97b2ad3c393f4146680b14e6ff9d05cc39f23d6ad15623` | `9dda440fbdcb69fda4f485ed39733d114bec9933a2c5a84024b86b01de26a9b3` | `https://apis.data.go.kr/1160100/GetStocDiviInfoService_V2/getDiviInfo_V2` |

Every pinned operation documents `serviceKey`, pagination, JSON/XML selection, and a JSON response
with header, body, paging metadata, and item records. The listed-instrument and both price operations
allow exact/range date and identifier filters. Issuance V3 and dividend V2 expose `basDt`, `crno`,
and company-name filters in their rendered Swagger/guide tables.

The four guides state a 4,000-byte maximum message size and 30 TPS for the relevant operations, but
the collector does not rely on those claims: every slot independently allows at most 218,000 bytes,
and the complete run is capped at 5 MiB with no concurrency or retry.

## Issuance V3 documentation conflict

[The Financial Services Commission mandatory-parameter notice](https://www.data.go.kr/en/bbs/ntc/selectNotice.do?originId=NOTICE_0000000004719),
SHA-256 `8c7e5f9b7122f691a0a6228246140619e7f48bc566b206d4d542c0cf30818fb7`,
names `basDt`, `isinCd`, and `crno` as the stock-basic-information selection parameters and says a
missing selection defaults to the latest `basDt`. The V3 guide repeats that prose, while its request
table omits `isinCd`; the rendered Swagger marks `basDt` required and likewise omits `isinCd`.

E1 does not guess which representation is authoritative. All V3 request slots provide `basDt`, do
not send the disputed `isinCd` parameter, and add only documented `crno` or company-name filters.
Any runtime rejection, silent latest-date default, or schema mismatch stops the run without retry.

## Rights evidence and decision

- [Portal policy](https://www.data.go.kr/ugs/selectPortalPolicyView.do), SHA-256
  `c2010f5030b2c9e7c58bd91bcc2ad105bb23a0205e55c104b0fabbaf91868d2b`, states
  that Public Nuri Type 2 requires attribution, permits noncommercial use, and permits derivative
  works.
- [Public Nuri Type 2 general certificate](https://www.kogl.or.kr/info/licenseType2.do),
  SHA-256 `73f9246b17b5df4505b3279c9f6e56d822abc2a127f9f8ad872784704aa97c9d`,
  grants online and offline sharing/use and derivative modification, subject to attribution and
  noncommercial use. It also states that a pre-change use may continue for that work without a
  change of purpose if the displayed conditions later change.
- Listed-instrument and stock-price pages display `이용허락범위 제한 없음`.
- Issuance and dividend pages display Public Nuri Type 2 and state that commercial use requires a
  separate KSD information-use agreement.
- All four pages describe capital-market analysis uses. Neither the publication pages nor the
  applicable general certificate states a deletion deadline for compliant retained evidence.

Engineering classification for this private noncommercial research probe:

| Use | Listed instruments / prices | Issuance / dividends |
| --- | --- | --- |
| Temporary local evidence for the bounded call | `documented` | `documented`, attribution required |
| Durable private raw retention | `documented` under the displayed unrestricted license | `documented` as offline noncommercial use, with attribution |
| Internal noncommercial backtest use | `documented` under the displayed unrestricted license; completeness remains a separate gate | `documented` as noncommercial derivative use, with attribution |
| Private derived-result retention | `documented` under displayed unrestricted license | `documented` for noncommercial derivatives with attribution |

These classifications do not authorize commercial use, third-party raw-data transfer, a public
dataset, an external API, or a paid report. They are an engineering gate, not legal advice. A
provider-specific term that conflicts with this table, a purpose change, or a license-condition
breach stops use. Any later commercial use requires a separate KSD agreement.

## Fixed identity evidence

- [KRX Hanjin Shipping delisting disclosure](https://kind.krx.co.kr/external/2017/02/17/000655/20170217001623/68051.htm),
  SHA-256 `9fa8beb85cec54fa628102c7030d4b8575b2b229ce248dc984ee4fb675197db8`,
  states short code `A117930`, final settlement-trading date 2017-03-06, and delisting date
  2017-03-07. The plan uses this fixed sample and permits no substitution.
- [Official KRX-filed report containing Samsung Electronics' corporation number](https://kind.krx.co.kr/external/2017/11/14/002561/20171114005530/11013.htm),
  SHA-256 `a498b839375dc7eac67406ce89e9c2f616f0a57e15138abaa975bcc644099be1`,
  records Samsung Electronics as `1301110006246`.
- Samsung Electronics ISIN `KR7005930003`, KODEX 200 ISIN `KR7069500007`, and the 2018 split dates
  are retained from the previously reviewed Gate D/Gate E0 evidence.

## Inspection limitation

The listing, issuance, and dividend DOCX guides rendered successfully for visual inspection. The
stock-price guide passed MIME/OOXML checks and complete text extraction, and its operation/parameter
tables matched the live rendered Swagger, but LibreOffice conversion did not terminate in two
bounded attempts. No fact in the plan relies solely on unrendered layout.
