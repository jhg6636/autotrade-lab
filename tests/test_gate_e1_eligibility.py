from __future__ import annotations

import json
import os
import socket
import urllib.error
from datetime import UTC, datetime
from email.message import Message
from pathlib import Path

import pytest

from autotrade_lab.gate_e1_eligibility import (
    OUTPUT_DIR,
    collect_gate_e1_eligibility,
    collect_gate_e1_eligibility_from_key_file,
    field_contract_sha256,
    gate_e1_eligibility_packet,
    gate_e1_eligibility_packet_sha256,
    verify_gate_e1_eligibility,
)
from autotrade_lab.gate_e1_prep import RequestSlot, gate_e1_request_plan


class FakeResponse:
    def __init__(self, body: bytes, *, url: str, headers: dict[str, str] | None = None):
        self.body = body
        self.url = url
        self.status = 200
        self.offset = 0
        self.headers = Message()
        self.headers["Content-Type"] = "application/json; charset=UTF-8"
        self.headers["Content-Length"] = str(len(body))
        self.headers["X-RateLimit-Limit"] = "10000"
        self.headers["X-RateLimit-Remaining"] = "9999"
        for key, value in (headers or {}).items():
            self.headers[key] = value

    def read(self, amount: int = -1) -> bytes:
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


def _isin(index: int) -> str:
    return f"KR7{index:09d}"


def _slot_isin(slot: RequestSlot, index: int) -> str:
    filters = dict(slot.filters)
    if "isinCd" in filters:
        return filters["isinCd"]
    if "samsung" in slot.request_id or filters.get("crno") == "1301110006246":
        return "KR7005930003"
    if "hanjin" in slot.request_id:
        return "KR7117930004"
    return _isin(index)


def _row(slot: RequestSlot, index: int) -> dict[str, str]:
    filters = dict(slot.filters)
    bas_dt = filters.get("basDt", "20251231")
    isin = _slot_isin(slot, index)
    short_code = f"A{index:06d}"
    if "likeSrtnCd" in filters:
        short_code = f"A{filters['likeSrtnCd']}"
    elif isin == "KR7005930003":
        short_code = "A005930"
    elif isin == "KR7069500007":
        short_code = "A069500"
    elif isin == "KR7117930004":
        short_code = "A117930"
    company = filters.get("stckIssuCmpyNm", "삼성전자(주)" if isin == "KR7005930003" else "회사")
    crno = filters.get("crno", "1301110006246" if isin == "KR7005930003" else "1101110000000")
    if isin == "KR7117930004":
        company = "(주)한진해운"
        crno = "1101110000017"

    common = {
        "basDt": bas_dt,
        "crno": crno,
        "isinCd": isin,
        "isinCdNm": "표본 종목",
        "itmsNm": "표본 종목",
        "mrktCtg": "KOSDAQ" if slot.request_id == "listing_kosdaq_sentinel" else "KOSPI",
        "srtnCd": short_code,
        "stckIssuCmpyNm": company,
    }
    if slot.operation == "/getItemInfo":
        return {**common, "corpNm": company}
    if slot.operation in {"/getStockPriceInfo", "/getSecuritiesPriceInfo"}:
        return {
            **common,
            "clpr": "11",
            "fltRt": "1.0",
            "hipr": "12",
            "lopr": "9",
            "mrktTotAmt": "11000000",
            "mkp": "10",
            "stLstgCnt": "1000000",
            "lstgStCnt": "1000000",
            "trPrc": "1100",
            "trqu": "100",
            "vs": "1",
        }
    if slot.operation == "/getItemBasiInfo_V3":
        return {
            **common,
            "issuStckCnt": "1000000",
            "dpsgCanDt": "",
            "dpsgRegDt": "19750611",
            "issuFrmtClsfNm": "일반",
            "itmsShrtnCd": short_code,
            "lstgAbolDt": "20170307" if "hanjin" in slot.request_id else "",
            "lstgDt": "19750611",
            "scrsItmsKcd": "01",
            "scrsItmsKcdNm": "보통주",
            "stckParPrc": "100",
        }
    if slot.operation == "/getStocIssuInfo_V3":
        return {
            **common,
            "issuStckCnt": "5000000",
            "lstgDt": "20180504",
            "scrsDcd": "01",
            "scrsItmsKcd": "01",
            "scrsItmsKcdNm": "보통주",
            "stckIssuDcnt": "1",
            "stckIssuDt": "20180504",
            "stckIssuSqno": "1",
            "stckIssuRcd": "01",
            "stckIssuRcdNm": "주식분할",
        }
    if slot.operation == "/getDiviInfo_V2":
        return {
            **common,
            "cashDvdnPayDt": "20260415",
            "cashGrdnDvdnRt": "0",
            "dvdnBasDt": "20251231",
            "scrsItmsKcd": "01",
            "scrsItmsKcdNm": "보통주",
            "stckDvdnRcd": "01",
            "stckDvdnRcdNm": "정기배당",
            "stckGenrCashDvdnRt": "2.5",
            "stckGenrDvdnAmt": "500",
            "stckGenrDvdnRt": "0",
            "stckGrdnDvdnAmt": "0",
            "stckGrdnDvdnRt": "0",
            "stckHndvDt": "",
            "stckParPrc": "100",
            "stckStacMd": "12",
            "trsnmDptyDcd": "01",
            "trsnmDptyDcdNm": "한국예탁결제원",
        }
    raise AssertionError(slot.operation)


class PacketTransport:
    def __init__(
        self,
        *,
        fail_ordinal: int | None = None,
        empty_ids: set[str] | None = None,
        mutate=None,
        response_headers: dict[str, str] | None = None,
        wrapped: bool = True,
    ):
        self.slots = gate_e1_request_plan()
        self.fail_ordinal = fail_ordinal
        self.empty_ids = empty_ids or set()
        self.mutate = mutate
        self.response_headers = response_headers
        self.wrapped = wrapped
        self.requests = []

    def open(self, request, *, timeout: float) -> FakeResponse:
        ordinal = len(self.requests) + 1
        self.requests.append(request)
        assert timeout == 30.0
        if ordinal == self.fail_ordinal:
            raise urllib.error.URLError(socket.gaierror("lookup failed"))
        slot = self.slots[ordinal - 1]
        if slot.request_id in self.empty_ids:
            rows = []
            total = 0
        elif slot.request_id in {"listing_probe_page_1", "stock_price_probe_page_1"}:
            rows = [_row(slot, index) for index in range(50)]
            total = 60
        elif slot.request_id in {"listing_probe_page_2", "stock_price_probe_page_2"}:
            rows = [_row(slot, index) for index in range(50, 60)]
            total = 60
        else:
            rows = [_row(slot, ordinal)]
            total = 1
        payload = {
            "response": {
                "body": {
                    "items": {"item": rows},
                    "numOfRows": str(slot.max_rows),
                    "pageNo": str(slot.page_no),
                    "totalCount": str(total),
                },
                "header": {"resultCode": "00", "resultMsg": "NORMAL SERVICE."},
            }
        }
        if self.mutate is not None:
            self.mutate(ordinal, slot, payload)
        if not self.wrapped:
            payload = payload["response"]
        body = json.dumps(payload, ensure_ascii=False).encode()
        return FakeResponse(body, url=request.full_url, headers=self.response_headers)


def _collect(tmp_path: Path, monkeypatch, transport: PacketTransport) -> tuple[dict, Path]:
    monkeypatch.chdir(tmp_path)
    manifest = collect_gate_e1_eligibility(
        OUTPUT_DIR,
        decoded_service_key="decoded/test+key",
        approved_packet_sha256=gate_e1_eligibility_packet_sha256(),
        transport=transport,
        now=lambda: datetime(2026, 8, 28, tzinfo=UTC),
    )
    return manifest, OUTPUT_DIR


def test_packet_hash_is_fresh_complete_and_pinned() -> None:
    packet = gate_e1_eligibility_packet()
    assert packet["packet_id"] == "gate-e1-eligibility-20260828-v1"
    assert packet["limits"] == {
        "concurrency": 1,
        "per_slot_raw_bytes": 218_000,
        "raw_bytes": 5 * 1024 * 1024,
        "requests": 24,
        "retries": 0,
        "rows": 1_200,
        "timeout_seconds": 30.0,
    }
    assert len(packet["requests"]) == 24
    assert field_contract_sha256() == (
        "fa60afc780c3dee48fa1e345477758925da1754f3c767f09a0f839e657f024bc"
    )
    assert gate_e1_eligibility_packet_sha256() == (
        "605df1d560b33116823f91033df324876a671cdec51ceb794630009452dd25b6"
    )


def test_complete_packet_is_verifiable_and_decisions_are_conservative(
    tmp_path: Path, monkeypatch
) -> None:
    transport = PacketTransport()
    manifest, run_dir = _collect(tmp_path, monkeypatch, transport)
    assert len(transport.requests) == 24
    assert manifest["terminal_state"] == "complete"
    assert manifest["observed"]["attempted_requests"] == 24
    assert manifest["pagination_checks"]["listing"]["status"] == "passed"
    assert manifest["pagination_checks"]["stock_price"]["status"] == "passed"
    assert manifest["eligibility"]["stock_daily"]["status"] == "feasible_for_e2"
    assert manifest["eligibility"]["etf_daily"]["status"] == "limited"
    assert manifest["eligibility"]["kodex200_single_instrument"]["status"] == "feasible_for_e2"
    assert manifest["eligibility"]["backtest_decision"] == "no_go"
    assert len(list((run_dir / "raw").iterdir())) == 24
    assert verify_gate_e1_eligibility(run_dir)["terminal_state"] == "complete"


def test_documented_top_level_envelope_works_for_all_six_operations(
    tmp_path: Path, monkeypatch
) -> None:
    manifest, run_dir = _collect(tmp_path, monkeypatch, PacketTransport(wrapped=False))
    assert manifest["terminal_state"] == "complete"
    assert {result["envelope"] for result in manifest["results"]} == {"documented_top_level"}
    verify_gate_e1_eligibility(run_dir)


@pytest.mark.parametrize("ordinal", [1, 12])
def test_transport_failure_writes_canonical_partial_manifest(
    tmp_path: Path, monkeypatch, ordinal: int
) -> None:
    transport = PacketTransport(fail_ordinal=ordinal)
    manifest, run_dir = _collect(tmp_path, monkeypatch, transport)
    assert len(transport.requests) == ordinal
    assert manifest["terminal_state"] == "stopped"
    assert manifest["stop"] == {"category": "transport", "ordinal": ordinal}
    assert manifest["results"][-1]["transport_category"] == "dns"
    assert len(list((run_dir / "raw").iterdir())) == ordinal - 1
    assert verify_gate_e1_eligibility(run_dir)["terminal_state"] == "stopped"


def test_semantic_filter_mismatch_stops_before_bad_raw_retention(
    tmp_path: Path, monkeypatch
) -> None:
    def mutate(ordinal, slot, payload):
        if ordinal == 2:
            payload["response"]["body"]["items"]["item"][0]["basDt"] = "20990101"

    manifest, run_dir = _collect(tmp_path, monkeypatch, PacketTransport(mutate=mutate))
    assert manifest["stop"] == {"category": "semantic_filter", "ordinal": 2}
    assert manifest["results"][-1]["provider_result_code"] == "00"
    assert manifest["results"][-1]["envelope"] == "observed_response_wrapper"
    assert len(list((run_dir / "raw").iterdir())) == 1
    verify_gate_e1_eligibility(run_dir)


@pytest.mark.parametrize(
    ("expected_category", "mutate"),
    [
        (
            "semantic_required_fields",
            lambda ordinal, slot, payload: payload["response"]["body"]["items"]["item"][0].pop(
                "corpNm"
            ),
        ),
        (
            "total_count",
            lambda ordinal, slot, payload: payload["response"]["body"].update(totalCount="0"),
        ),
        (
            "semantic_ohlcv",
            lambda ordinal, slot, payload: (
                payload["response"]["body"]["items"]["item"][0].update(hipr="8")
                if ordinal == 7
                else None
            ),
        ),
    ],
)
def test_required_fields_total_count_and_ohlcv_fail_closed(
    tmp_path: Path, monkeypatch, expected_category: str, mutate
) -> None:
    if expected_category == "semantic_ohlcv":
        expected_ordinal = 7
    else:
        expected_ordinal = 1

    def targeted(ordinal, slot, payload):
        if ordinal == expected_ordinal:
            mutate(ordinal, slot, payload)

    manifest, run_dir = _collect(tmp_path, monkeypatch, PacketTransport(mutate=targeted))
    assert manifest["stop"] == {"category": expected_category, "ordinal": expected_ordinal}
    assert len(list((run_dir / "raw").iterdir())) == expected_ordinal - 1
    verify_gate_e1_eligibility(run_dir)


def test_provider_error_is_fixed_and_provider_message_is_not_retained(
    tmp_path: Path, monkeypatch
) -> None:
    def mutate(ordinal, slot, payload):
        payload["response"]["header"] = {
            "resultCode": "30",
            "resultMsg": "provider-controlled detail must not persist",
        }

    manifest, run_dir = _collect(tmp_path, monkeypatch, PacketTransport(mutate=mutate))
    result = manifest["results"][0]
    assert manifest["stop"] == {"category": "provider_result_code", "ordinal": 1}
    assert result["provider_result_code"] == "30"
    assert result["response_sha256"] is not None
    persisted = (run_dir / "manifest.json").read_bytes()
    assert b"provider-controlled" not in persisted
    assert not list((run_dir / "raw").iterdir())
    verify_gate_e1_eligibility(run_dir)


def test_malformed_provider_code_is_schema_failure_with_verifiable_manifest(
    tmp_path: Path, monkeypatch
) -> None:
    def mutate(ordinal, slot, payload):
        payload["response"]["header"]["resultCode"] = "SUCCESS"

    manifest, run_dir = _collect(tmp_path, monkeypatch, PacketTransport(mutate=mutate))
    assert manifest["stop"] == {"category": "schema", "ordinal": 1}
    assert manifest["results"][0]["provider_result_code"] is None
    verify_gate_e1_eligibility(run_dir)


def test_non_utf8_json_is_fixed_invalid_json_failure(tmp_path: Path, monkeypatch) -> None:
    class NonUtf8Transport(PacketTransport):
        def open(self, request, *, timeout: float) -> FakeResponse:
            self.requests.append(request)
            return FakeResponse(b'\xff{"response":{}}', url=request.full_url)

    manifest, run_dir = _collect(tmp_path, monkeypatch, NonUtf8Transport())
    assert manifest["stop"] == {"category": "invalid_json", "ordinal": 1}
    verify_gate_e1_eligibility(run_dir)


def test_deeply_nested_json_is_fixed_invalid_json_failure(tmp_path: Path, monkeypatch) -> None:
    class DeepJsonTransport(PacketTransport):
        def open(self, request, *, timeout: float) -> FakeResponse:
            self.requests.append(request)
            body = b"[" * 100_000 + b"0" + b"]" * 100_000
            return FakeResponse(body, url=request.full_url)

    manifest, run_dir = _collect(tmp_path, monkeypatch, DeepJsonTransport())
    assert manifest["stop"] == {"category": "invalid_json", "ordinal": 1}
    verify_gate_e1_eligibility(run_dir)


@pytest.mark.parametrize(
    "body,category",
    [
        (b"1" * 5000, "invalid_json"),
        (
            b'{"header":{"resultCode":"00"},"body":{"pageNo":"1","numOfRows":"50","totalCount":1e100000}}',
            "total_count",
        ),
    ],
)
def test_extreme_json_numbers_leave_terminal_manifest(tmp_path, monkeypatch, body, category):
    class NumericTransport(PacketTransport):
        def open(self, request, *, timeout):
            self.requests.append(request)
            return FakeResponse(body, url=request.full_url)

    manifest, run_dir = _collect(tmp_path, monkeypatch, NumericTransport())
    assert manifest["stop"] == {"category": category, "ordinal": 1}
    verify_gate_e1_eligibility(run_dir)


def test_streamed_byte_overflow_records_actual_probe_byte(tmp_path: Path, monkeypatch) -> None:
    class ByteOverflowTransport(PacketTransport):
        def open(self, request, *, timeout: float) -> FakeResponse:
            self.requests.append(request)
            response = FakeResponse(b"x" * 218_001, url=request.full_url)
            del response.headers["Content-Length"]
            return response

    manifest, run_dir = _collect(tmp_path, monkeypatch, ByteOverflowTransport())
    assert manifest["stop"] == {"category": "byte_budget", "ordinal": 1}
    assert manifest["results"][0]["response_bytes"] == 218_001
    assert manifest["observed"]["response_bytes_read"] == 218_001
    verify_gate_e1_eligibility(run_dir)

    manifest["results"][0]["response_bytes"] = 1
    manifest["observed"]["response_bytes_read"] = 1
    (run_dir / "manifest.json").write_bytes(
        (
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode()
    )
    with pytest.raises(ValueError, match="byte-budget failure"):
        verify_gate_e1_eligibility(run_dir)


def test_verifier_rejects_impossible_redirect_failure_shape(tmp_path: Path, monkeypatch) -> None:
    class RedirectTransport(PacketTransport):
        def open(self, request, *, timeout: float) -> FakeResponse:
            self.requests.append(request)
            return FakeResponse(b"{}", url="https://apis.data.go.kr/wrong")

    manifest, run_dir = _collect(tmp_path, monkeypatch, RedirectTransport())
    assert manifest["stop"] == {"category": "redirect", "ordinal": 1}
    verify_gate_e1_eligibility(run_dir)

    manifest["results"][0].update(http_status=418, response_bytes=1, response_sha256="0" * 64)
    manifest["observed"]["response_bytes_read"] = 1
    (run_dir / "manifest.json").write_bytes(
        (
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode()
    )
    with pytest.raises(ValueError, match="pre-body failure"):
        verify_gate_e1_eligibility(run_dir)


def test_verifier_rejects_failure_category_impossible_for_slot(tmp_path: Path, monkeypatch) -> None:
    def mutate(ordinal, slot, payload):
        payload["response"]["body"]["items"]["item"][0].pop("corpNm")

    manifest, run_dir = _collect(tmp_path, monkeypatch, PacketTransport(mutate=mutate))
    assert manifest["stop"] == {"category": "semantic_required_fields", "ordinal": 1}
    manifest["results"][0]["failure_category"] = "semantic_ohlcv"
    manifest["stop"]["category"] = "semantic_ohlcv"
    (run_dir / "manifest.json").write_bytes(
        (
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode()
    )
    with pytest.raises(ValueError, match="impossible failure category"):
        verify_gate_e1_eligibility(run_dir)


def test_secret_in_json_body_stops_without_raw_retention(tmp_path: Path, monkeypatch) -> None:
    def mutate(ordinal, slot, payload):
        payload["response"]["header"]["resultMsg"] = "decoded/test+key"

    manifest, run_dir = _collect(tmp_path, monkeypatch, PacketTransport(mutate=mutate))
    assert manifest["stop"] == {"category": "secret_body", "ordinal": 1}
    persisted = (run_dir / "manifest.json").read_bytes()
    assert b"decoded/test+key" not in persisted
    assert not list((run_dir / "raw").iterdir())
    verify_gate_e1_eligibility(run_dir)


def test_pagination_total_mismatch_and_duplicate_stop(tmp_path: Path, monkeypatch) -> None:
    def total_mutation(ordinal, slot, payload):
        if slot.request_id == "listing_probe_page_2":
            payload["response"]["body"]["totalCount"] = "61"

    manifest, _ = _collect(tmp_path, monkeypatch, PacketTransport(mutate=total_mutation))
    assert manifest["stop"] == {"category": "pagination_total_mismatch", "ordinal": 4}

    other = tmp_path / "other"
    other.mkdir()

    def duplicate_mutation(ordinal, slot, payload):
        if slot.request_id == "listing_probe_page_2":
            payload["response"]["body"]["items"]["item"][0] = _row(slot, 0)

    manifest, _ = _collect(other, monkeypatch, PacketTransport(mutate=duplicate_mutation))
    assert manifest["stop"] == {"category": "pagination_duplicate", "ordinal": 4}


def test_empty_historical_boundary_yields_limited_stock_without_failure(
    tmp_path: Path, monkeypatch
) -> None:
    manifest, run_dir = _collect(
        tmp_path,
        monkeypatch,
        PacketTransport(empty_ids={"listing_2010_boundary"}),
    )
    assert manifest["terminal_state"] == "complete"
    assert manifest["eligibility"]["stock_daily"]["status"] == "limited"
    assert "historical_2010_listing" in manifest["eligibility"]["stock_daily"]["blockers"]
    verify_gate_e1_eligibility(run_dir)


def test_disjoint_current_listing_and_price_isins_cannot_pass_stock(
    tmp_path: Path, monkeypatch
) -> None:
    def mutate(ordinal, slot, payload):
        if slot.request_id == "stock_price_probe_page_1":
            for index, row in enumerate(payload["response"]["body"]["items"]["item"]):
                row["isinCd"] = _isin(index + 1_000)

    manifest, run_dir = _collect(tmp_path, monkeypatch, PacketTransport(mutate=mutate))
    assert manifest["terminal_state"] == "complete"
    assert manifest["eligibility"]["stock_daily"]["status"] == "failed"
    assert "current_listing_and_price" in manifest["eligibility"]["stock_daily"]["blockers"]
    verify_gate_e1_eligibility(run_dir)


def test_unexercised_listing_page_pair_is_not_reported_as_passed(
    tmp_path: Path, monkeypatch
) -> None:
    def mutate(ordinal, slot, payload):
        body = payload["response"]["body"]
        if slot.request_id == "listing_probe_page_1":
            body["items"]["item"] = body["items"]["item"][:1]
            body["totalCount"] = "1"
        elif slot.request_id == "listing_probe_page_2":
            body["items"]["item"] = []
            body["totalCount"] = "1"

    manifest, run_dir = _collect(tmp_path, monkeypatch, PacketTransport(mutate=mutate))
    assert manifest["terminal_state"] == "complete"
    assert manifest["pagination_checks"]["listing"]["status"] == "not_exercised"
    assert manifest["eligibility"]["stock_daily"]["status"] == "limited"
    verify_gate_e1_eligibility(run_dir)


def test_header_secret_stops_immediately_without_persisting_secret(
    tmp_path: Path, monkeypatch
) -> None:
    manifest, run_dir = _collect(
        tmp_path,
        monkeypatch,
        PacketTransport(response_headers={"Retry-After": "decoded%2Ftest%2Bkey"}),
    )
    assert manifest["stop"] == {"category": "secret_header", "ordinal": 1}
    persisted = (run_dir / "manifest.json").read_bytes()
    assert b"decoded/test+key" not in persisted
    assert b"decoded%2Ftest%2Bkey" not in persisted
    assert not list((run_dir / "raw").iterdir())
    verify_gate_e1_eligibility(run_dir)


def test_lowercase_percent_encoded_header_secret_is_rejected(tmp_path: Path, monkeypatch) -> None:
    manifest, run_dir = _collect(
        tmp_path,
        monkeypatch,
        PacketTransport(response_headers={"Retry-After": "decoded%2ftest%2bkey"}),
    )
    assert manifest["stop"] == {"category": "secret_header", "ordinal": 1}
    persisted = (run_dir / "manifest.json").read_bytes()
    assert b"decoded%2ftest%2bkey" not in persisted
    verify_gate_e1_eligibility(run_dir)


def test_hash_and_existing_output_fail_before_transport_or_key_read(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    transport = PacketTransport()
    with pytest.raises(PermissionError, match="hash"):
        collect_gate_e1_eligibility(
            OUTPUT_DIR,
            decoded_service_key="decoded/test+key",
            approved_packet_sha256="0" * 64,
            transport=transport,
        )
    assert not transport.requests
    assert not OUTPUT_DIR.exists()

    OUTPUT_DIR.mkdir(parents=True)
    with pytest.raises(FileExistsError, match="never reuse"):
        collect_gate_e1_eligibility_from_key_file(
            OUTPUT_DIR,
            key_file=Path("missing-key-file"),
            approved_packet_sha256=gate_e1_eligibility_packet_sha256(),
            transport=transport,
        )


def test_verifier_rejects_manifest_and_raw_tamper(tmp_path: Path, monkeypatch) -> None:
    manifest, run_dir = _collect(tmp_path, monkeypatch, PacketTransport())
    manifest_path = run_dir / "manifest.json"
    original_manifest = manifest_path.read_bytes()
    manifest["limits"]["retries"] = 1
    manifest_path.write_bytes(
        (
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode()
    )
    with pytest.raises(ValueError, match="invalid Gate E1 eligibility manifest"):
        verify_gate_e1_eligibility(run_dir)
    manifest_path.write_bytes(original_manifest)

    raw = next((run_dir / "raw").iterdir())
    raw.write_bytes(b"{}")
    with pytest.raises(ValueError, match="raw evidence mismatch"):
        verify_gate_e1_eligibility(run_dir)


def test_key_file_path_is_private_when_packet_runs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    key_file = Path(".env.public-data")
    key_file.write_text("PUBLIC_DATA_SERVICE_KEY_DECODED=decoded/test+key\n")
    os.chmod(key_file, 0o600)
    manifest = collect_gate_e1_eligibility_from_key_file(
        OUTPUT_DIR,
        key_file=key_file,
        approved_packet_sha256=gate_e1_eligibility_packet_sha256(),
        transport=PacketTransport(fail_ordinal=1),
    )
    assert manifest["stop"] == {"category": "transport", "ordinal": 1}
