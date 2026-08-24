from __future__ import annotations

import json
import urllib.parse
from datetime import UTC, datetime, timedelta
from email.message import Message
from pathlib import Path

from autotrade_lab.gate_d2_probe import (
    MASTER_WAIT_SECONDS,
    MAX_CANDLE_ROWS,
    MAX_MARKET_DATA_REQUESTS,
    collect_gate_d2,
    verify_gate_d2,
)


class FakeResponse:
    def __init__(self, body: bytes):
        self.body = body
        self.status = 200
        self.headers = Message()
        self.headers["Content-Type"] = "application/json"
        self.headers["X-RateLimit-Limit"] = "1"

    def read(self, amount: int = -1) -> bytes:
        return self.body[:amount] if amount >= 0 else self.body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


class FakeTransport:
    def __init__(self):
        self.urls: list[str] = []

    def open(self, request, *, timeout: float) -> FakeResponse:
        assert timeout == 30.0
        assert request.get_header("Authorization") == "Bearer test-token"
        assert request.get_header("X-tossinvest-account") is None
        self.urls.append(request.full_url)
        parsed = urllib.parse.urlparse(request.full_url)
        params = urllib.parse.parse_qs(parsed.query)
        if parsed.path.endswith("/candles"):
            count = int(params["count"][0])
            payload = {
                "result": {
                    "candles": [
                        {
                            "timestamp": f"2026-08-24T00:{index:02d}:00+09:00",
                            "closePrice": "1",
                        }
                        for index in range(count)
                    ],
                    "nextBefore": "2026-08-23T00:00:00+09:00",
                }
            }
        elif parsed.path.endswith("/stocks/all"):
            status = params["status"][0]
            payload = {
                "result": (
                    [{"symbol": "000010"}, {"symbol": "000005"}] if status == "DELISTED" else []
                )
            }
        elif parsed.path.endswith("/stocks"):
            payload = {"result": [{"symbol": symbol} for symbol in params["symbols"][0].split(",")]}
        else:
            payload = {"result": {"today": {"date": "2018-05-04"}}}
        return FakeResponse(json.dumps(payload).encode())


def test_gate_d2_is_exact_bounded_and_does_not_persist_token(tmp_path: Path) -> None:
    transport = FakeTransport()
    waits: list[float] = []
    current = datetime(2026, 8, 24, tzinfo=UTC)

    def now() -> datetime:
        nonlocal current
        value = current
        current += timedelta(seconds=1)
        return value

    manifest = collect_gate_d2(
        tmp_path / "probe",
        access_token="test-token",
        transport=transport,
        wait=waits.append,
        now=now,
    )
    assert manifest["observed"]["attempted_requests"] == MAX_MARKET_DATA_REQUESTS
    assert manifest["observed"]["candle_rows"] == MAX_CANDLE_ROWS
    assert manifest["selected_delisted_symbol"] == "000005"
    assert waits == [MASTER_WAIT_SECONDS] * 3
    assert len(transport.urls) == MAX_MARKET_DATA_REQUESTS
    assert all("order" not in url and "account" not in url for url in transport.urls)
    persisted = b"".join(
        path.read_bytes() for path in (tmp_path / "probe").rglob("*") if path.is_file()
    )
    assert b"test-token" not in persisted
    requests = manifest["requests"]
    assert requests[1]["params"]["before"] == "2026-08-23T00:00:00+09:00"
    assert requests[3]["params"]["before"] == "2026-08-23T00:00:00+09:00"
    assert requests[-2]["params"]["symbols"] == "005930,000005"
    assert verify_gate_d2(tmp_path / "probe") == manifest["observed"]


def test_gate_d2_verifier_rejects_changed_raw_evidence(tmp_path: Path) -> None:
    collect_gate_d2(
        tmp_path / "probe",
        access_token="test-token",
        transport=FakeTransport(),
        wait=lambda _: None,
        now=lambda: datetime(2026, 8, 24, tzinfo=UTC),
    )
    raw = next((tmp_path / "probe/raw").iterdir())
    raw.write_bytes(b"{}")
    try:
        verify_gate_d2(tmp_path / "probe")
    except ValueError as error:
        assert "checksum mismatch" in str(error)
    else:
        raise AssertionError("changed raw evidence was accepted")


def test_gate_d2_verifier_recomputes_candle_rows(tmp_path: Path) -> None:
    run_dir = tmp_path / "probe"
    collect_gate_d2(
        run_dir,
        access_token="test-token",
        transport=FakeTransport(),
        wait=lambda _: None,
        now=lambda: datetime(2026, 8, 24, tzinfo=UTC),
    )
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["requests"][0]["observed_candle_rows"] = 99
    manifest["observed"]["candle_rows"] = 799
    manifest_path.write_text(json.dumps(manifest))
    try:
        verify_gate_d2(run_dir)
    except ValueError as error:
        assert "candle row mismatch" in str(error)
    else:
        raise AssertionError("false candle row count was accepted")
