# Gate E0 — Korean research-data source resolution

- Base commit: `64e088f`
- Working branch: `agent/GATE-E0-source-resolution`
- Retrieval date: 2026-08-24 KST
- Stage: complete — reviewed official-source and data-rights plan

## Objective and boundaries

Gate E0 selects the smallest plausible official-source combination for survivorship-aware Korean
stock and ETF research. It does not collect API data, create API keys, accept terms, purchase data,
backtest, rank strategies, modify canonical records, access accounts, place orders, or trade.

An API's technical reachability is separate from permission to retain and use its data. A current
symbol list is separate from a historical point-in-time universe. A corporate-action announcement
is separate from an effective adjustment factor. `Documented`, `conditional`, `unknown`, and
`inaccessible` retain those distinctions.

## Decision criteria

A source is admitted to a later feasibility probe only when official material identifies:

1. the instrument class and fields it claims to cover;
2. official license metadata sufficient to admit a bounded feasibility call, while keeping durable
   storage and backtest rights unknown until detailed conditions are fingerprinted;
3. a bounded access mechanism and quota;
4. candidate stable identifiers that might join source records without name matching, with
   sufficiency explicitly deferred to E1;
5. every unresolved history, lifecycle, correction, or corporate-action semantic recorded as
   `conditional`, `unknown`, or `inaccessible` rather than silently filled.

No source is promoted merely because it has an endpoint, a download button, or a successful sample.

## Official-source matrix

| Source | Documented value | Rights and access | Gate E0 decision |
| --- | --- | --- | --- |
| [Toss canonical OpenAPI](https://openapi.tossinvest.com/openapi-docs/latest/openapi.json) and [developer guide](https://developers.tossinvest.com/docs) | Execution-compatible current instruments; `1m`/`1d` candles; documented cursor/timestamp mechanics. Gate D2 observed old daily access and one split adjustment. | Market-data local retention, derived use, and redistribution remain undocumented. Guaranteed retention, daily session scope, and complete adjustment method remain unknown. | Keep for execution compatibility and later current-data checks. Do not use as the historical research source. |
| [KRX Open API service list](https://openapi.krx.co.kr/contents/OPP/INFO/service/OPPINFO004.cmd) | KOSPI/KOSDAQ stock and ETF daily trading data from 2010-01-04; stock basic information from the same boundary. | [Open API terms](https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO002.jsp) allow noncommercial use only, prohibit third-party provision, require attribution for screens, limit a key to 10,000 requests/day, and prohibit use of received information after contract termination. Durable storage and internal backtest rights during the contract are not expressly granted. | Reject as the default durable research archive. Retain only as an official capability/reference and possible separately contracted fallback. |
| [KIND historical listed-issue status](https://kind.krx.co.kr/corpgeneral/listedIssueStatus.do?method=loadInitPage) and [delisting status](https://kind.krx.co.kr/investwarn/delcompany.do?method=searchDelCompanyMain) | Listed-issue status exposes a query date; delisting status exposes market and period filters. | Exact dynamic output schema, correction history, ETF inclusion, and reusable-data rights were not established from the public pages. | Audit/reference only. Do not scrape or use as the primary dataset in E1. |
| [Financial Services Commission KRX listed-instrument API](https://www.data.go.kr/data/15094775/openapi.do) | Daily-batch `basDt`, short code, ISIN, market, item name, corporation number/name; free; 10,000 development calls; automatic approval. | Portal metadata displays `이용허락범위 제한 없음`. The published time range is blank; durable storage/backtest conditions, historical depth, delisted retention, and ETF coverage are not established. | Point-in-time-universe field candidate for a bounded feasibility call only. |
| [Financial Services Commission stock-price API](https://www.data.go.kr/data/15094808/openapi.do) | Separate stock and investment-security operations expose daily open/high/low/close/volume fields by date/code; free; 10,000 development calls; automatic approval. | Portal metadata displays `이용허락범위 제한 없음`. The time range and durable storage/backtest conditions are not established. Adjusted prices, factors, corrections, timezone, and suspended/no-trade semantics are undocumented. | Raw daily-price field candidate for a bounded feasibility call only. |
| [Financial Services Commission stock-issuance API](https://www.data.go.kr/data/15043423/openapi.do) | Basic issue fields include face value, shares, listing/delisting dates; issuance fields include date, round, reason, and share counts. Daily batch; free; 10,000 development calls. | Public Nuri Type 2: attribution and noncommercial use only; derivatives are allowed by portal policy. Commercial use requires a KSD agreement. Time range, durable storage conditions, and ETF coverage are not documented. | Stock lifecycle/capital-change field candidate for a bounded noncommercial feasibility call. |
| [Financial Services Commission stock-dividend API](https://www.data.go.kr/data/15043284/openapi.do) | Dividend record date, cash payment date, stock delivery date, amount/rate, share type, and reason. Daily batch; free; 10,000 development calls. | Public Nuri Type 2: attribution and noncommercial use only; derivatives are allowed by portal policy. Commercial use requires a KSD agreement. Time range and durable storage conditions are not documented. | Dividend field candidate for a bounded noncommercial feasibility call. |
| [OpenDART introduction](https://opendart.fss.or.kr/intro/main.do), [terms](https://opendart.fss.or.kr/intro/terms.do), and [guides](https://opendart.fss.or.kr/guide/main.do) | Anyone may download disclosure XML and extract/use desired material. Current `corp_code`/`stock_code`; filing timestamps/corrections; 2015+ structured fields for some bonus issues, capital reductions, mergers, and company divisions. | Free in principle; authentication key required; key sharing prohibited. Research use and processing are supported, but long-term retention and external raw/derived redistribution are not expressly defined. Structured domestic listing/delisting, stock split/reverse split, executable cash-dividend events, and historical code validity are incomplete. | Supporting authority for identity, announcement, ratio, and correction evidence. Never use as the point-in-time universe or sole adjustment source. |
| [SEIBro ETF information](https://m.seibro.or.kr/cnts/etf/selectPublishInfo.do) | Current ETF issue/detail views. | Historical lifecycle API, history range, and reusable-data conditions were not established from the official public material reviewed. | Reject for E1. Consider only after a documented open dataset or separately reviewed KSD agreement. |
| KRX/KOSCOM contracted EOD products | Contract products advertise close, instrument-event, settlement, investor, and index data, including ETF products. | Product schema, backfill period, price, storage, non-display analysis, and termination rights require login, quotation, and contract review. | Paid fallback only. Stop and return to the user before contacting, purchasing, or accepting terms. |

## Important rights conclusion

The KRX Open API terms apply to that direct service and are not silently applied to a separate
official Public Data Portal publication. Conversely, portal license metadata does not by itself
prove that no provider-specific condition exists, that indefinite raw retention is allowed, or that
the data are complete. Gate E1-PREP must fingerprint the official guides, portal policy, displayed
license, and any provider-specific conditions before any data call. Until then, long-term raw
storage and backtest use remain `unknown` for all four candidates.

This is an engineering gate, not legal advice. Any commercial deployment, third-party dataset,
external API, public raw-data release, or paid report requires a fresh rights decision.

## Coverage decision by executable track

| Track | Decision | Reason |
| --- | --- | --- |
| Korean listed stocks, daily | **Conditional GO to Gate E1-PREP only** | The four portal APIs expose candidate fields for universe, raw OHLCV, lifecycle/capital changes, and dividends. Detailed conditions, history, and completeness remain untested. |
| Korean listed ETFs, daily | **NO-GO** | Daily prices may be present, but a complete historical ETF listing/delisting lifecycle and identifier-change source is not documented. |
| Korean listed stocks/ETFs, one minute | **NO-GO** | Toss retention, daily/intraday session attribution, and data-use rights remain unresolved; no admitted alternative one-minute archive was found. |
| Toss live/current execution compatibility | **Planning only** | Toss remains the intended broker/current reference. No account/order API or trading action is authorized. |

This conditional decision does not authorize a backtest. It authorizes the user to review a small
data-feasibility probe that can still fail closed.

## Minimum candidate source set

For a possible noncommercial Korean **stock daily** feasibility test:

1. `KRX상장종목정보` — date-keyed ISIN/code/market membership candidate;
2. `주식발행정보` — listing/delisting and capital-change candidate;
3. `주식시세정보` — raw daily OHLCV candidate;
4. `주식배당정보` — dividend event candidate;
5. OpenDART — a later independent filing/correction source after the portal dataset is feasible.

The first four are a minimum candidate set, not an admitted dataset. OpenDART is intentionally
excluded from the first data-call budget: its bulk company-code file can exceed the row budget and
targeted corporate-action endpoints require a pre-resolved `corp_code`. Bulk `corpCode.xml` is
forbidden in E1. Toss is absent from the historical candidate set and is used only for later
execution mapping.

## Gate E1 proposed two-step feasibility gate — not authorized

### E1-PREP — documentation and collector packet only

E1-PREP makes no data request and requires no key. It must:

1. retrieve and fingerprint the four official Swagger definitions/guides and portal policy;
2. record exact base URLs, operations, parameters, result models, license metadata, and any
   provider-specific conditions;
3. decide whether temporary local evidence, durable raw retention, internal backtest use, and
   derived-output retention are each documented, conditional, or unknown;
4. implement an allowlisted collector whose 24 immutable slots each declare operation, filters,
   `pageNo`, `numOfRows=50`, and maximum response bytes before execution;
5. redact `serviceKey` from URLs, logs, exceptions, and manifests and stream response bodies with a
   hard cumulative 5 MiB cutoff;
6. add fake-transport tests for row, byte, page, endpoint, redirect, secret, and stop conditions;
7. produce the exact E1-DATA request table for a second user review.

If any official guide or detailed condition remains unavailable, E1-PREP stops. Completing E1-PREP
does not authorize E1-DATA.

### E1-DATA — bounded calls after a second explicit approval

### Preconditions

- The user separately approves the completed E1-PREP packet and creation/use of a Public Data Portal
  service key.
- The key is supplied through a private mode-`0600`, Git-ignored file; it is never printed,
  committed, included in a URL manifest/log, or delegated through chat.
- Only the four portal APIs are allowlisted. No OpenDART bulk/API request, direct KRX Open API, KIND
  scrape, SEIBro scrape, or Toss request is allowed.

### Hard budget

- At most **24 data requests total**, attempted once each;
- every slot fixes `numOfRows=50`; at most **1,200 returned records** and **5 MiB** of raw response
  bodies across all 24 slots;
- each fixed query/filter combination may not advance beyond page 2; page-2 requests are allowed
  only in the two pagination slots named below;
- no retry, automatic pagination, broad date sweep, or reuse of prior unused budget;
- the response reader checks a valid `Content-Length` against remaining budget when present, reads in
  bounded chunks, and aborts before retaining bytes past the cumulative limit;
- raw-body retention is allowed only if E1-PREP documents it. Otherwise E1-DATA does not start.

### Deterministic samples

1. Active KOSPI stock: Samsung Electronics `005930` / ISIN `KR7005930003`.
2. KOSDAQ sentinel: short code `196170`, admitted only if the portal returns an explicit KOSDAQ
   market and ISIN identity; otherwise stop rather than name-match.
3. ETF coverage sentinel: KODEX 200 `069500` / ISIN `KR7069500007`.
4. Corporate-action breakpoint: Samsung Electronics' 2018 50-for-1 split window, used only as a
   known cross-source observation.
5. Delisted stock: the E1-PREP packet must name the exact issuance operation and fixed filter. From
   `pageNo=1&numOfRows=50`, sort locally by `(ISIN, short code)` and select the first non-null
   delisting date. Make exactly one pre-delist price request; no row means the sample fails and is not
   replaced.

### Request allocation

| Purpose | Maximum requests |
| --- | ---: |
| Listed-instrument `/GetKrxListedInfoService/getItemInfo`, including one page-2 check | 6 |
| Stock-price `/GetStockSecuritiesInfoService/getStockPriceInfo`, including one page-2 check | 6 |
| Investment-security `/GetStockSecuritiesInfoService/getSecuritiesPriceInfo` ETF sentinel | 2 |
| Issuance operations resolved and pinned by E1-PREP | 6 |
| Dividend operation resolved and pinned by E1-PREP | 4 |
| **Total** | **24** |

Every slot uses `pageNo=1`, `numOfRows=50`, and `resultType=json` except the two predeclared page-2
slots. Exact filters must be pinned in E1-PREP and their maximum rows sum to 1,200. A missing operation
or parameter stops E1-PREP instead of being invented.

### Required observations

- presence or absence at the preselected 2009-12-31 and 2010-01-04 boundaries, explicitly recorded
  as observations rather than a guaranteed earliest date;
- whether a date-keyed listing snapshot retains delisted instruments and whether active/delisted
  membership agrees with issuance listing/delisting dates;
- whether the ETF sentinel appears in both listing and price services, and whether its security type
  is explicit rather than inferred from its name;
- ISIN, short-code, and corporation-number joinability without name matching; DART `corp_code`
  mapping is deferred to a later audited corporate-action stage;
- treatment of trading halts, zero-volume listed days, missing days, duplicate rows, corrected rows,
  code changes, and delist boundaries;
- raw versus adjusted price meaning and whether any factor/event feed is available;
- dividend record/payment dates and share-class identity;
- runtime quota headers/errors without retry.

| Observation | Assigned slots | Passing evidence | If absent |
| --- | --- | --- | --- |
| 2009/2010/current listing history | listed-instrument date slots | returned `basDt` and stable ISIN/code fields | stock daily remains `limited` or `failed`; never infer earliest history |
| Delisted membership | issuance first page, one listing boundary, one price boundary | fixed sample has delist date plus pre-delist identity/price | PIT stock track `failed`; do not substitute |
| ETF identity | listed-instrument plus investment-security slots | explicit ISIN and security/market identity joins without name matching | ETF track `failed` |
| Split/raw-price behavior | Samsung event stock-price and issuance slots | source fields explain the observed discontinuity or adjustment status | adjustment remains `unknown`; only raw-price feasibility may be `limited` |
| Dividend identity | four dividend slots | record/payment dates and share-class identifier join | total-return track `failed` |
| Pagination | listed-instrument and stock-price page-2 slots | stable total/page metadata, no duplicate identity | affected service `failed` |

Trading halts, zero-volume rows, corrections, code changes, withdrawals, and other corporate-action
types are adversarial cases, not guaranteed observations. If a preselected sample does not expose
one, record `not_observed`; the affected dimension cannot be called complete or usable.

### Completion conditions

Gate E1 is complete only when:

1. every tracked record validates against a pinned schema and source license;
2. the manifest reproduces byte/count/hash results from local raw files;
3. no credential, raw body, account data, or machine-specific secret path is tracked;
4. stock-daily and ETF-daily receive separate `feasible_for_E2`, `limited`, or `failed` decisions;
5. no observed fact is promoted to a documented guarantee;
6. canonical strategy/index files remain unchanged;
7. no backtest, ranking, optimization, paper order, or live order occurs.

### Stop conditions

Stop before further calls or normalization if:

- a displayed license, detailed guide, or provider condition conflicts with the plan, or durable
  evidence/backtest use remains unknown at the end of E1-PREP;
- a key is missing, printed, group/world-readable, symlinked, or appears in a request URL/artifact;
- the request, row, page, or byte budget would be exceeded;
- any endpoint redirects outside its official allowlist, returns account data, or requires a paid
  purchase/terms acceptance not already reviewed;
- historical filters silently default to current records or preselected-date behavior cannot be
  distinguished from a genuine empty result;
- no deterministic delisted-stock sample or no explicit ETF identity can be obtained;
- ISIN/code/corporation joins require a name-based guess;
- a 429, authentication, schema, checksum, pagination, or rights error occurs;
- resolving the issue would require a retry, broader collection, manual sample substitution, direct
  KRX/KIND/SEIBro scraping, Toss market data, or any trading API.

## Gate E0 conclusion

Gate E0 is complete as a reviewed plan. The most token- and rights-efficient next move is E1-PREP,
not a data call, broad KRX/Toss collection, or strategy backtest. E1-DATA remains closed until
E1-PREP produces an exact immutable request table and the user approves it separately.
