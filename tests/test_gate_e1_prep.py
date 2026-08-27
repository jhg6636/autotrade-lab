from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.parse
from collections import Counter
from dataclasses import replace
from datetime import UTC, datetime
from email.message import Message
from pathlib import Path

import pytest

from autotrade_lab.gate_e1_prep import (
    MAX_RAW_BYTES,
    MAX_REQUESTS,
    MAX_ROWS,
    MAX_SLOT_BYTES,
    GateE1Stop,
    collect_gate_e1_connectivity_recovery,
    collect_gate_e1_data,
    gate_e1_connectivity_recovery_plan,
    gate_e1_connectivity_recovery_sha256,
    gate_e1_plan_sha256,
    gate_e1_request_plan,
    load_public_data_service_key,
    validate_gate_e1_plan,
    verify_gate_e1_connectivity_recovery,
    verify_gate_e1_data,
)


class FakeResponse:
    def __init__(
        self,
        body: bytes,
        *,
        url: str,
        status: int = 200,
        content_type: str = "application/json",
        content_length: int | None = None,
    ):
        self.body = body
        self.status = status
        self.url = url
        self.offset = 0
        self.read_calls = 0
        self.headers = Message()
        self.headers["Content-Type"] = content_type
        if content_length is not None:
            self.headers["Content-Length"] = str(content_length)

    def read(self, amount: int = -1) -> bytes:
        self.read_calls += 1
        if amount < 0:
            amount = len(self.body) - self.offset
        result = self.body[self.offset : self.offset + amount]
        self.offset += len(result)
        return result

    def geturl(self) -> str:
        return self.url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


def _payload(page_no: int, num_rows: int, rows: list[dict] | None = None) -> bytes:
    return json.dumps(
        {
            "header": {"resultCode": "00", "resultMsg": "NORMAL SERVICE."},
            "body": {
                "numOfRows": str(num_rows),
                "pageNo": str(page_no),
                "totalCount": str(len(rows or [])),
                "items": {"item": rows or []},
            },
        }
    ).encode()


def _write_manifest(path: Path, manifest: dict) -> None:
    path.write_bytes(
        (
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode()
    )


class FakeTransport:
    def __init__(self):
        self.requests = []

    def open(self, request, *, timeout: float) -> FakeResponse:
        assert timeout == 30.0
        self.requests.append(request)
        parsed = urllib.parse.urlparse(request.full_url)
        params = urllib.parse.parse_qs(parsed.query)
        assert params["serviceKey"] == ["decoded/test+key"]
        body = _payload(
            int(params["pageNo"][0]),
            int(params["numOfRows"][0]),
            [{"basDt": params.get("basDt", ["unknown"])[0], "isinCd": "KR7005930003"}],
        )
        return FakeResponse(body, url=request.full_url, content_length=len(body))


class OneResponseTransport:
    def __init__(self, response_factory):
        self.response_factory = response_factory
        self.requests = []
        self.response = None

    def open(self, request, *, timeout: float) -> FakeResponse:
        self.requests.append(request)
        self.response = self.response_factory(request)
        return self.response


def test_request_plan_is_exact_bounded_and_fully_filtered() -> None:
    slots = gate_e1_request_plan()
    assert len(slots) == MAX_REQUESTS
    assert sum(slot.max_rows for slot in slots) == MAX_ROWS
    assert sum(slot.max_response_bytes for slot in slots) <= MAX_RAW_BYTES
    assert all(slot.max_rows == 50 and slot.filters for slot in slots)
    assert {slot.request_id for slot in slots if slot.page_no == 2} == {
        "listing_probe_page_2",
        "stock_price_probe_page_2",
    }
    assert Counter(slot.service for slot in slots) == {
        "listed_instruments": 6,
        "stock_price": 7,
        "investment_security_price": 2,
        "stock_issuance": 6,
        "stock_dividend": 3,
    }
    assert all(slot.safe_record["base_url"] == slot.base_url for slot in slots)
    assert gate_e1_plan_sha256() == (
        "ae802b8d4245a153af5abea3e2875049ee086e6556541ff3f8f1a5d2677198f0"
    )


def test_plan_rejects_endpoint_page_and_budget_mutation() -> None:
    slots = list(gate_e1_request_plan())
    slots[0] = replace(slots[0], base_url="https://example.com/private/orders")
    with pytest.raises(ValueError, match="not allowlisted"):
        validate_gate_e1_plan(tuple(slots))

    slots = list(gate_e1_request_plan())
    slots[0] = replace(slots[0], page_no=2)
    with pytest.raises(ValueError, match="page-2"):
        validate_gate_e1_plan(tuple(slots))

    slots = list(gate_e1_request_plan())
    slots[0] = replace(slots[0], max_response_bytes=MAX_RAW_BYTES)
    with pytest.raises(ValueError, match="5 MiB"):
        validate_gate_e1_plan(tuple(slots))


def test_service_key_file_requires_private_mode_exact_name_and_no_symlink(tmp_path: Path) -> None:
    path = tmp_path / ".env.public-data"
    path.write_text("PUBLIC_DATA_SERVICE_KEY_DECODED=decoded/test+key\n")
    os.chmod(path, 0o600)
    assert load_public_data_service_key(path) == "decoded/test+key"

    os.chmod(path, 0o644)
    with pytest.raises(PermissionError, match="group or others"):
        load_public_data_service_key(path)
    os.chmod(path, 0o600)

    link = tmp_path / "key-link"
    link.symlink_to(path)
    with pytest.raises(ValueError, match="non-symlink"):
        load_public_data_service_key(link)

    path.write_text("PUBLIC_DATA_SERVICE_KEY=wrong-name\n")
    with pytest.raises(ValueError, match="exactly"):
        load_public_data_service_key(path)


def test_request_injects_key_only_into_live_url_not_safe_record() -> None:
    slot = gate_e1_request_plan()[0]
    request = slot.request("decoded/test+key")
    parsed = urllib.parse.urlparse(request.full_url)
    assert urllib.parse.parse_qs(parsed.query)["serviceKey"] == ["decoded/test+key"]
    assert "serviceKey" not in json.dumps(slot.safe_record)
    assert request.get_header("Authorization") is None
    assert request.method == "GET"
    assert "account" not in parsed.path and "order" not in parsed.path


def test_collection_uses_all_slots_once_and_never_persists_key(tmp_path: Path) -> None:
    transport = FakeTransport()
    run_dir = tmp_path / "gate-e1"
    manifest = collect_gate_e1_data(
        run_dir,
        decoded_service_key="decoded/test+key",
        approved_plan_sha256=gate_e1_plan_sha256(),
        transport=transport,
        now=lambda: datetime(2026, 8, 24, tzinfo=UTC),
    )
    assert len(transport.requests) == MAX_REQUESTS
    assert manifest["observed"]["attempted_requests"] == MAX_REQUESTS
    assert manifest["observed"]["rows"] == MAX_REQUESTS
    assert len(list((run_dir / "raw").glob("*.json"))) == MAX_REQUESTS
    persisted = b"".join(path.read_bytes() for path in run_dir.rglob("*") if path.is_file())
    assert b"decoded/test+key" not in persisted
    assert b"serviceKey" not in persisted
    assert verify_gate_e1_data(run_dir) == manifest["observed"]


def test_collection_rejects_url_encoded_key_in_selected_header(tmp_path: Path) -> None:
    class HeaderEchoTransport(FakeTransport):
        def open(self, request, *, timeout: float) -> FakeResponse:
            response = super().open(request, timeout=timeout)
            response.headers["Retry-After"] = "decoded%2Ftest%2Bkey"
            return response

    run_dir = tmp_path / "gate-e1"
    with pytest.raises(GateE1Stop, match="manifest boundary"):
        collect_gate_e1_data(
            run_dir,
            decoded_service_key="decoded/test+key",
            approved_plan_sha256=gate_e1_plan_sha256(),
            transport=HeaderEchoTransport(),
        )
    assert not (run_dir / "manifest.json").exists()
    persisted = b"".join(path.read_bytes() for path in run_dir.rglob("*") if path.is_file())
    assert b"decoded/test+key" not in persisted
    assert b"decoded%2Ftest%2Bkey" not in persisted


def test_collection_requires_exact_approved_plan_before_creating_output(tmp_path: Path) -> None:
    run_dir = tmp_path / "gate-e1"
    with pytest.raises(PermissionError, match="explicitly approved"):
        collect_gate_e1_data(
            run_dir,
            decoded_service_key="decoded/test+key",
            approved_plan_sha256="0" * 64,
            transport=FakeTransport(),
        )
    assert not run_dir.exists()


def test_declared_oversize_stops_before_read_or_retention(tmp_path: Path) -> None:
    body = _payload(1, 50)
    transport = OneResponseTransport(
        lambda request: FakeResponse(
            body,
            url=request.full_url,
            content_length=MAX_SLOT_BYTES + 1,
        )
    )
    with pytest.raises(GateE1Stop, match="declared response"):
        collect_gate_e1_data(
            tmp_path / "run",
            decoded_service_key="decoded/test+key",
            approved_plan_sha256=gate_e1_plan_sha256(),
            transport=transport,
        )
    assert transport.response.read_calls == 0
    assert not list((tmp_path / "run/raw").iterdir())


def test_streaming_oversize_stops_without_retaining_extra_byte(tmp_path: Path) -> None:
    body = b"x" * (MAX_SLOT_BYTES + 1)
    transport = OneResponseTransport(lambda request: FakeResponse(body, url=request.full_url))
    with pytest.raises(GateE1Stop, match="response exceeds"):
        collect_gate_e1_data(
            tmp_path / "run",
            decoded_service_key="decoded/test+key",
            approved_plan_sha256=gate_e1_plan_sha256(),
            transport=transport,
        )
    assert transport.response.offset == MAX_SLOT_BYTES + 1
    assert not list((tmp_path / "run/raw").iterdir())


def test_redirect_secret_echo_and_row_overflow_fail_before_retention(tmp_path: Path) -> None:
    redirect = OneResponseTransport(
        lambda request: FakeResponse(_payload(1, 50), url="https://example.com/redirect")
    )
    with pytest.raises(GateE1Stop, match="redirected"):
        collect_gate_e1_data(
            tmp_path / "redirect",
            decoded_service_key="decoded/test+key",
            approved_plan_sha256=gate_e1_plan_sha256(),
            transport=redirect,
        )

    echo = OneResponseTransport(
        lambda request: FakeResponse(b'{"error":"decoded/test+key"}', url=request.full_url)
    )
    with pytest.raises(GateE1Stop, match="echoed"):
        collect_gate_e1_data(
            tmp_path / "echo",
            decoded_service_key="decoded/test+key",
            approved_plan_sha256=gate_e1_plan_sha256(),
            transport=echo,
        )

    overflow = OneResponseTransport(
        lambda request: FakeResponse(
            _payload(1, 50, [{"row": index} for index in range(51)]),
            url=request.full_url,
        )
    )
    with pytest.raises(GateE1Stop, match="row budget"):
        collect_gate_e1_data(
            tmp_path / "rows",
            decoded_service_key="decoded/test+key",
            approved_plan_sha256=gate_e1_plan_sha256(),
            transport=overflow,
        )
    for name in ("redirect", "echo", "rows"):
        assert not list((tmp_path / name / "raw").iterdir())


def test_schema_page_and_content_type_fail_closed_without_retry(tmp_path: Path) -> None:
    cases = (
        (
            "page",
            lambda request: FakeResponse(_payload(2, 50), url=request.full_url),
            "paging metadata",
        ),
        (
            "schema",
            lambda request: FakeResponse(b'{"unexpected":true}', url=request.full_url),
            "schema",
        ),
        (
            "content",
            lambda request: FakeResponse(
                _payload(1, 50), url=request.full_url, content_type="text/html"
            ),
            "content type",
        ),
    )
    for name, factory, message in cases:
        transport = OneResponseTransport(factory)
        with pytest.raises(GateE1Stop, match=message):
            collect_gate_e1_data(
                tmp_path / name,
                decoded_service_key="decoded/test+key",
                approved_plan_sha256=gate_e1_plan_sha256(),
                transport=transport,
            )
        assert len(transport.requests) == 1


def test_network_failure_does_not_retain_secret_exception_context(tmp_path: Path) -> None:
    class FailingTransport:
        def open(self, request, *, timeout: float):
            raise urllib.error.URLError(f"failed URL {request.full_url}")

    with pytest.raises(GateE1Stop, match="network or transport") as caught:
        collect_gate_e1_data(
            tmp_path / "network",
            decoded_service_key="decoded/test+key",
            approved_plan_sha256=gate_e1_plan_sha256(),
            transport=FailingTransport(),
        )
    assert caught.value.__context__ is None
    assert "decoded/test+key" not in repr(caught.value)


def test_verifier_rejects_changed_raw_evidence_and_false_totals(tmp_path: Path) -> None:
    run_dir = tmp_path / "gate-e1"
    collect_gate_e1_data(
        run_dir,
        decoded_service_key="decoded/test+key",
        approved_plan_sha256=gate_e1_plan_sha256(),
        transport=FakeTransport(),
        now=lambda: datetime(2026, 8, 24, tzinfo=UTC),
    )
    raw_path = next((run_dir / "raw").iterdir())
    original = raw_path.read_bytes()
    raw_path.write_bytes(b"{}")
    with pytest.raises(ValueError, match="byte count mismatch"):
        verify_gate_e1_data(run_dir)
    raw_path.write_bytes(original)

    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["observed"]["rows"] += 1
    _write_manifest(manifest_path, manifest)
    with pytest.raises(ValueError, match="totals"):
        verify_gate_e1_data(run_dir)


def test_verifier_rejects_manifest_metadata_outcome_limits_and_extra_raw(tmp_path: Path) -> None:
    run_dir = tmp_path / "gate-e1"
    collect_gate_e1_data(
        run_dir,
        decoded_service_key="decoded/test+key",
        approved_plan_sha256=gate_e1_plan_sha256(),
        transport=FakeTransport(),
        now=lambda: datetime(2026, 8, 24, tzinfo=UTC),
    )
    manifest_path = run_dir / "manifest.json"
    original = manifest_path.read_bytes()

    manifest = json.loads(original)
    manifest["requests"][0]["base_url"] = "https://example.com"
    _write_manifest(manifest_path, manifest)
    with pytest.raises(ValueError, match="metadata mismatch"):
        verify_gate_e1_data(run_dir)

    manifest = json.loads(original)
    manifest["requests"][0]["status"] = 201
    _write_manifest(manifest_path, manifest)
    with pytest.raises(ValueError, match="outcome mismatch"):
        verify_gate_e1_data(run_dir)

    manifest = json.loads(original)
    manifest["limits"]["retries"] = 1
    _write_manifest(manifest_path, manifest)
    with pytest.raises(ValueError, match="invalid Gate E1 manifest"):
        verify_gate_e1_data(run_dir)

    manifest_path.write_bytes(original)
    (run_dir / "raw" / "unexpected.json").write_text("{}")
    with pytest.raises(ValueError, match="raw-file set"):
        verify_gate_e1_data(run_dir)


def test_connectivity_recovery_plan_is_fresh_single_and_bounded() -> None:
    slot = gate_e1_connectivity_recovery_plan()
    assert slot.request_id == "connectivity_listing_2010_boundary"
    assert slot.filters == (("basDt", "20100104"),)
    assert slot.page_no == 1
    assert slot.max_rows == 1
    assert slot.max_response_bytes == 65_536
    assert gate_e1_connectivity_recovery_sha256() == (
        "1740ba05109d918f4ccbcf72bca361749c8e1607dc91a0ca4db4476c347f5279"
    )
    assert gate_e1_connectivity_recovery_sha256() != gate_e1_plan_sha256()


def test_connectivity_recovery_records_dns_failure_without_secret(tmp_path: Path) -> None:
    class DnsFailureTransport:
        def __init__(self):
            self.requests = []

        def open(self, request, *, timeout: float):
            self.requests.append(request)
            raise urllib.error.URLError(socket.gaierror("name lookup failed"))

    transport = DnsFailureTransport()
    run_dir = tmp_path / "recovery"
    report = collect_gate_e1_connectivity_recovery(
        run_dir,
        decoded_service_key="decoded/test+key",
        approved_plan_sha256=gate_e1_connectivity_recovery_sha256(),
        transport=transport,
        now=lambda: datetime(2026, 8, 27, tzinfo=UTC),
    )
    assert len(transport.requests) == 1
    assert report["result"]["outcome"] == "transport_error"
    assert report["result"]["transport_category"] == "dns"
    assert not list((run_dir / "raw").iterdir())
    persisted = (run_dir / "result.json").read_bytes()
    assert b"decoded/test+key" not in persisted
    assert b"serviceKey" not in persisted
    assert verify_gate_e1_connectivity_recovery(run_dir) == report["result"]


def test_connectivity_recovery_success_is_verifiable_and_single_request(tmp_path: Path) -> None:
    transport = FakeTransport()
    run_dir = tmp_path / "recovery"
    report = collect_gate_e1_connectivity_recovery(
        run_dir,
        decoded_service_key="decoded/test+key",
        approved_plan_sha256=gate_e1_connectivity_recovery_sha256(),
        transport=transport,
        now=lambda: datetime(2026, 8, 27, tzinfo=UTC),
    )
    assert len(transport.requests) == 1
    assert report["result"]["outcome"] == "success"
    assert report["result"]["observed_rows"] == 1
    assert len(list((run_dir / "raw").iterdir())) == 1
    assert verify_gate_e1_connectivity_recovery(run_dir) == report["result"]


def test_connectivity_recovery_distinguishes_http_error_and_rejects_tamper(
    tmp_path: Path,
) -> None:
    class HttpFailureTransport:
        def open(self, request, *, timeout: float):
            headers = Message()
            headers["Content-Type"] = "application/json"
            raise urllib.error.HTTPError(request.full_url, 401, "unauthorized", headers, None)

    run_dir = tmp_path / "recovery"
    report = collect_gate_e1_connectivity_recovery(
        run_dir,
        decoded_service_key="decoded/test+key",
        approved_plan_sha256=gate_e1_connectivity_recovery_sha256(),
        transport=HttpFailureTransport(),
        now=lambda: datetime(2026, 8, 27, tzinfo=UTC),
    )
    assert report["result"]["outcome"] == "http_error"
    assert report["result"]["http_status"] == 401
    assert report["result"]["transport_category"] is None
    assert verify_gate_e1_connectivity_recovery(run_dir) == report["result"]

    report["result"]["unexpected"] = True
    _write_manifest(run_dir / "result.json", report)
    with pytest.raises(ValueError, match="invalid connectivity-recovery result"):
        verify_gate_e1_connectivity_recovery(run_dir)


def test_connectivity_recovery_requires_fresh_approval_hash(tmp_path: Path) -> None:
    with pytest.raises(PermissionError, match="explicitly approved"):
        collect_gate_e1_connectivity_recovery(
            tmp_path / "recovery",
            decoded_service_key="decoded/test+key",
            approved_plan_sha256=gate_e1_plan_sha256(),
            transport=FakeTransport(),
        )
    assert not (tmp_path / "recovery").exists()
