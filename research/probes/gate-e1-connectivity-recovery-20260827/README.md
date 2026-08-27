# Gate E1 connectivity-recovery result

The separately approved one-request packet reached the Financial Services Commission listed-
instrument endpoint and received HTTP 200 with JSON content type. The response failed the pinned
normal-data schema and was classified as `schema_error`. No retry occurred and the nonconforming
body was not retained.

Authoritative local evidence is `result.json`:

- one attempt, zero retries;
- HTTP 200;
- quota limit 10,000 and remaining 9,999;
- zero retained raw bodies, rows, or body bytes;
- no credential, live URL, account data, order, or trade.

Interpretation: network and HTTP reachability are observed. Successful authentication, exact
provider result code/envelope, historical coverage, and data usability remain unobserved. Do not
rerun this packet or infer a Gate E1-DATA pass.
