# Gate C Phase 2 — Toss market-data-only execution record

## Exact request plan

The user confirmed the local mode-0600 credential file and allowed IP. The collector then executed
this exact plan once. See `research/probes/gate-c-toss-20260824/README.md` for the result; do not run
the command again as part of this Gate C review.

- nine candle requests: four symbols × adjusted `1d`/`1m`, plus unadjusted Samsung Electronics
  `1d`; at most 1,800 candle rows;
- four stock-master snapshots: KOSPI/KOSDAQ × ACTIVE/DELISTED;
- one four-symbol detail request;
- one Korean market-calendar request for 2026-08-24;
- 15 market-data requests total. Combined with Phase 1: 27/29 requests and at most
  10,600/10,600 candle rows.

Allowed symbols are `005930`, `000660`, `069500`, and `229200`. Allowed paths are only
`/api/v1/candles`, `/api/v1/stocks/all`, `/api/v1/stocks`, and
`/api/v1/market-calendar/KR`. Account, asset, holding, buying-power, commission, order,
conditional-order, and every private/account header are forbidden.

## Secret preparation

Do not paste credentials into chat or commit them. In a local terminal from the repository root,
create the already-Git-ignored `.env.toss` as a mode-0600 regular file:

```zsh
umask 077
read -rs 'TOSS_CLIENT_ID?Toss client ID: '
printf '\n'
read -rs 'TOSS_CLIENT_SECRET?Toss client secret: '
printf '\nTOSS_CLIENT_ID=%s\nTOSS_CLIENT_SECRET=%s\n' \
  "$TOSS_CLIENT_ID" "$TOSS_CLIENT_SECRET" > .env.toss
unset TOSS_CLIENT_ID TOSS_CLIENT_SECRET
chmod 600 .env.toss
```

Before collection, the user must also confirm that the current outbound IP is registered in Toss
WTS Open API settings. The command performs one OAuth client-credentials issuance in memory; the
official API states that reissuing invalidates the prior token for that client. Neither client
credentials nor the access token are written to manifests or response artifacts. If a response
echoes any credential, persistence stops before writing the body.

## Authorized command after confirmation

```zsh
.venv/bin/python -m autotrade_lab.data_probe collect-toss \
  research/probes/gate-c-toss-20260824 \
  research/probes/gate-c-public-crypto-20260824 \
  --credentials-file .env.toss
```

Do not execute it until the user confirms both the secret file and allowed-IP registration.
