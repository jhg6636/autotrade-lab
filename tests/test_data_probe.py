from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from email.message import Message
from pathlib import Path

import pytest

from autotrade_lab.data_probe import (
    CRYPTO_MAX_ROWS,
    CRYPTO_REQUESTS,
    MAX_REQUESTS,
    MAX_ROWS,
    TOSS_MAX_ROWS,
    TOSS_REQUESTS,
    ProbeRequest,
    build_normalized_artifacts,
    build_toss_http_requests,
    build_toss_normalized_artifacts,
    collect_crypto,
    collect_toss,
    crypto_probe_requests,
    issue_toss_access_token,
    load_toss_client_credentials,
    normalize_crypto,
    normalize_toss,
    toss_probe_requests,
    validate_crypto_plan,
    verify_crypto,
    verify_toss,
)


class FakeResponse:
    def __init__(self, body: bytes):
        self.body = body
        self.status = 200
        self.headers = Message()
        self.headers["Content-Type"] = "application/json"
        self.headers["X-MBX-USED-WEIGHT-1M"] = "12"

    def read(self, amount: int = -1) -> bytes:
        return self.body[:amount] if amount >= 0 else self.body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


class FakeTransport:
    def __init__(self):
        self.requests: list[urllib.request.Request] = []

    def open(self, request: urllib.request.Request, *, timeout: float) -> FakeResponse:
        assert timeout == 30
        self.requests.append(request)
        if "upbit.com" in request.full_url:
            parsed = urllib.parse.urlparse(request.full_url)
            market = urllib.parse.parse_qs(parsed.query)["market"][0]
            previous_time = (
                "2026-08-23T00:00:00" if parsed.path.endswith("/days") else "2026-08-23T23:00:00"
            )
            body = [
                {
                    "market": market,
                    "candle_date_time_utc": "2026-08-24T00:00:00",
                    "opening_price": 100,
                    "high_price": 110,
                    "low_price": 90,
                    "trade_price": 105,
                    "candle_acc_trade_price": 1000,
                    "candle_acc_trade_volume": 10,
                },
                {
                    "market": market,
                    "candle_date_time_utc": previous_time,
                    "opening_price": 90,
                    "high_price": 105,
                    "low_price": 80,
                    "trade_price": 100,
                    "candle_acc_trade_price": 900,
                    "candle_acc_trade_volume": 9,
                },
            ]
        else:
            body = [
                [
                    1787529600000,
                    "100",
                    "110",
                    "90",
                    "105",
                    "10",
                    1787533199999,
                    "1000",
                    20,
                    "5",
                    "500",
                    "0",
                ]
            ]
        return FakeResponse(json.dumps(body).encode())


class FakeTossTransport:
    def __init__(self):
        self.requests: list[urllib.request.Request] = []

    def open(self, request: urllib.request.Request, *, timeout: float) -> FakeResponse:
        assert timeout == 30
        self.requests.append(request)
        if "/candles?" in request.full_url:
            interval = urllib.parse.parse_qs(urllib.parse.urlparse(request.full_url).query)[
                "interval"
            ][0]
            timestamp = (
                "2026-08-24T00:00:00+09:00" if interval == "1d" else "2026-08-24T09:00:00+09:00"
            )
            body = {
                "result": {
                    "candles": [
                        {
                            "timestamp": timestamp,
                            "openPrice": "100",
                            "highPrice": "110",
                            "lowPrice": "90",
                            "closePrice": "105",
                            "volume": "10",
                            "currency": "KRW",
                        }
                    ]
                }
            }
        else:
            body = {"result": []}
        return FakeResponse(json.dumps(body).encode())


class EchoingTossTransport:
    def open(self, request: urllib.request.Request, *, timeout: float) -> FakeResponse:
        return FakeResponse(b'{"error":"test-token"}')


class FakeOAuthTransport:
    def __init__(self):
        self.request: urllib.request.Request | None = None

    def open(self, request: urllib.request.Request, *, timeout: float) -> FakeResponse:
        self.request = request
        body = {"access_token": "issued-token", "token_type": "Bearer", "expires_in": 3600}
        return FakeResponse(json.dumps(body).encode())


def fixed_now() -> datetime:
    return datetime(2026, 8, 24, 2, tzinfo=UTC)


def test_crypto_plan_is_exact_and_public() -> None:
    requests = crypto_probe_requests()
    assert len(requests) == CRYPTO_REQUESTS
    assert sum(item.max_rows for item in requests) == CRYPTO_MAX_ROWS
    assert {item.instrument_type for item in requests} == {"spot", "perpetual"}
    assert {item.interval for item in requests} == {"1h", "1d"}
    assert all(item.url.startswith("https://") for item in requests)


def test_plan_rejects_non_allowlisted_endpoint() -> None:
    bad = ProbeRequest(
        request_id="bad",
        provider="bad",
        venue="bad",
        instrument_type="spot",
        symbol="BTC",
        interval="1h",
        base_url="https://example.com/private/orders",
        params=(),
        max_rows=1,
    )
    with pytest.raises(ValueError, match="exactly 12"):
        validate_crypto_plan((bad,))
    valid = list(crypto_probe_requests())
    valid[0] = bad
    with pytest.raises(ValueError, match="not allowlisted"):
        validate_crypto_plan(tuple(valid))


def test_toss_plan_uses_only_market_data_and_fits_combined_budget() -> None:
    requests = toss_probe_requests()
    assert len(requests) == TOSS_REQUESTS
    assert sum(item.max_rows for item in requests) == TOSS_MAX_ROWS
    assert CRYPTO_REQUESTS + TOSS_REQUESTS <= MAX_REQUESTS
    assert CRYPTO_MAX_ROWS + TOSS_MAX_ROWS == MAX_ROWS
    assert sum(item.base_url.endswith("/candles") for item in requests) == 9
    assert all("order" not in item.base_url for item in requests)
    assert all("account" not in item.base_url for item in requests)
    assert all("holding" not in item.base_url for item in requests)


def test_toss_http_requests_use_bearer_but_never_account_header() -> None:
    requests = build_toss_http_requests("test-token")
    assert len(requests) == TOSS_REQUESTS
    assert all(request.get_header("Authorization") == "Bearer test-token" for request in requests)
    assert all(request.get_header("X-tossinvest-account") is None for request in requests)
    with pytest.raises(ValueError, match="invalid Toss access token"):
        build_toss_http_requests("bad\nheader")


def test_toss_credentials_file_requires_private_mode_and_exact_keys(tmp_path: Path) -> None:
    path = tmp_path / ".env.toss"
    path.write_text("TOSS_CLIENT_ID=id\nTOSS_CLIENT_SECRET=secret=value\n")
    os.chmod(path, 0o600)
    assert load_toss_client_credentials(path) == ("id", "secret=value")
    os.chmod(path, 0o644)
    with pytest.raises(PermissionError, match="group or others"):
        load_toss_client_credentials(path)
    os.chmod(path, 0o600)
    link = tmp_path / "credentials-link"
    link.symlink_to(path)
    with pytest.raises(ValueError, match="non-symlink"):
        load_toss_client_credentials(link)


def test_toss_oauth_token_is_returned_but_not_in_metadata() -> None:
    transport = FakeOAuthTransport()
    token, metadata = issue_toss_access_token("client-id", "client-secret", transport=transport)
    assert token == "issued-token"
    assert "issued-token" not in json.dumps(metadata)
    assert metadata["credentials_persisted"] is False
    assert metadata["token_persisted"] is False
    assert transport.request is not None
    assert transport.request.method == "POST"
    assert transport.request.full_url == "https://openapi.tossinvest.com/oauth2/token"
    assert transport.request.get_header("Authorization") is None


def test_toss_oauth_refuses_echoed_client_secret() -> None:
    with pytest.raises(RuntimeError, match="echoed a credential"):
        issue_toss_access_token("client-id", "test-token", transport=EchoingTossTransport())


def test_toss_collection_is_bounded_and_does_not_persist_token(tmp_path: Path) -> None:
    crypto_dir = tmp_path / "crypto"
    collect_crypto(crypto_dir, transport=FakeTransport(), now=fixed_now)
    toss_dir = tmp_path / "toss"
    transport = FakeTossTransport()
    waits: list[float] = []
    manifest = collect_toss(
        toss_dir,
        access_token="test-token",
        crypto_run_dir=crypto_dir,
        transport=transport,
        now=fixed_now,
        wait=waits.append,
    )
    assert manifest["observed"]["attempted_requests"] == TOSS_REQUESTS
    assert manifest["observed"]["candle_rows"] == 9
    assert manifest["observed"]["combined_attempted_requests"] == 27
    assert len(transport.requests) == TOSS_REQUESTS
    assert waits == [1.1, 1.1, 1.1]
    assert all(request.get_header("X-tossinvest-account") is None for request in transport.requests)
    assert b"test-token" not in (toss_dir / "manifest.json").read_bytes()


def test_toss_collection_refuses_echoed_token_before_persisting_body(tmp_path: Path) -> None:
    crypto_dir = tmp_path / "crypto"
    collect_crypto(crypto_dir, transport=FakeTransport(), now=fixed_now)
    toss_dir = tmp_path / "toss"
    with pytest.raises(RuntimeError, match="echoed a credential"):
        collect_toss(
            toss_dir,
            access_token="test-token",
            crypto_run_dir=crypto_dir,
            transport=EchoingTossTransport(),
            now=fixed_now,
            wait=lambda _: None,
        )
    assert not list(toss_dir.rglob("*.json"))


def test_collection_has_no_auth_and_is_bounded(tmp_path: Path) -> None:
    transport = FakeTransport()
    run_dir = tmp_path / "run"
    manifest = collect_crypto(run_dir, transport=transport, now=fixed_now)
    assert manifest["observed"]["attempted_requests"] == CRYPTO_REQUESTS
    assert manifest["observed"]["successful_requests"] == CRYPTO_REQUESTS
    assert len(transport.requests) == CRYPTO_REQUESTS
    assert all(request.method == "GET" for request in transport.requests)
    assert all(request.get_header("Authorization") is None for request in transport.requests)
    assert len(list((run_dir / "raw").glob("*.json"))) == CRYPTO_REQUESTS
    with pytest.raises(FileExistsError):
        collect_crypto(run_dir, transport=transport, now=fixed_now)


def test_normalization_is_byte_deterministic(tmp_path: Path) -> None:
    pytest.importorskip("pyarrow")
    run_dir = tmp_path / "run"
    collect_crypto(run_dir, transport=FakeTransport(), now=fixed_now)
    first = build_normalized_artifacts(run_dir)
    second = build_normalized_artifacts(run_dir)
    assert first == second
    report = normalize_crypto(run_dir)
    assert report["attempted_requests"] == CRYPTO_REQUESTS
    assert report["duplicate_keys"] == 0
    assert report["normalized_rows"] == 16
    assert report["structural_quality_pass"] is True
    assert verify_crypto(run_dir)["parquet_sha256"] == report["parquet_sha256"]


def test_toss_normalization_is_byte_deterministic_and_reports_reference_results(
    tmp_path: Path,
) -> None:
    pytest.importorskip("pyarrow")
    crypto_dir = tmp_path / "crypto"
    collect_crypto(crypto_dir, transport=FakeTransport(), now=fixed_now)
    toss_dir = tmp_path / "toss"
    collect_toss(
        toss_dir,
        access_token="test-token",
        crypto_run_dir=crypto_dir,
        transport=FakeTossTransport(),
        now=fixed_now,
        wait=lambda _: None,
    )
    first = build_toss_normalized_artifacts(toss_dir)
    second = build_toss_normalized_artifacts(toss_dir)
    assert first == second
    report = normalize_toss(toss_dir)
    assert report["normalized_rows"] == 9
    assert report["structural_quality_pass"] is True
    assert report["combined_attempted_requests"] == 27
    assert report["combined_candle_rows"] == 25
    assert len(report["reference_requests"]) == 6
    assert verify_toss(toss_dir)["parquet_sha256"] == report["parquet_sha256"]


def test_toss_raw_checksum_tampering_fails(tmp_path: Path) -> None:
    crypto_dir = tmp_path / "crypto"
    collect_crypto(crypto_dir, transport=FakeTransport(), now=fixed_now)
    toss_dir = tmp_path / "toss"
    collect_toss(
        toss_dir,
        access_token="test-token",
        crypto_run_dir=crypto_dir,
        transport=FakeTossTransport(),
        now=fixed_now,
        wait=lambda _: None,
    )
    first_raw = min((toss_dir / "raw").glob("*.json"))
    first_raw.write_bytes(b"{}")
    with pytest.raises(ValueError, match="Toss raw checksum mismatch"):
        build_toss_normalized_artifacts(toss_dir)


def test_raw_checksum_tampering_fails(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    collect_crypto(run_dir, transport=FakeTransport(), now=fixed_now)
    first_raw = min((run_dir / "raw").glob("*.json"))
    first_raw.write_bytes(b"[]")
    with pytest.raises(ValueError, match="raw checksum mismatch"):
        build_normalized_artifacts(run_dir)


def test_manifest_cannot_redirect_normalizer(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    collect_crypto(run_dir, transport=FakeTransport(), now=fixed_now)
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["requests"][0]["raw_path"] = "../../outside.json"
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="unexpected raw path"):
        build_normalized_artifacts(run_dir)


def test_manifest_cannot_change_provider_identity(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    collect_crypto(run_dir, transport=FakeTransport(), now=fixed_now)
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["requests"][0]["provider"] = "attacker"
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="does not match allowlist"):
        build_normalized_artifacts(run_dir)
