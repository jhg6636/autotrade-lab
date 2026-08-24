from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from autotrade_lab.market_data_contract import (
    TOSS_KR_DATA_CONTRACT,
    CandleInterval,
    DelistBoundary,
    EvidenceStatus,
    GateEBlocker,
    TimestampMeaning,
    derive_one_minute_bounds,
    gate_e_blockers,
    is_daily_session_complete,
    is_individually_listed_on,
    require_aware_timestamp,
    require_daily_session_end,
    safe_request_spacing_seconds,
    validate_candle_page,
    validate_cursor_progression,
    validate_descending_page,
)


def stamp(hour: int = 9, minute: int = 0) -> datetime:
    return datetime(2026, 8, 24, hour, minute, tzinfo=UTC)


def naive_stamp(hour: int = 9, minute: int = 0) -> datetime:
    return datetime(2026, 8, 24, hour, minute)  # noqa: DTZ001


def seoul_stamp(hour: int = 9, minute: int = 0) -> datetime:
    return datetime(2026, 8, 24, hour, minute, tzinfo=ZoneInfo("Asia/Seoul"))


def test_toss_contract_encodes_documented_facts() -> None:
    contract = TOSS_KR_DATA_CONTRACT

    assert set(EvidenceStatus) == {
        EvidenceStatus.DOCUMENTED,
        EvidenceStatus.OBSERVED,
        EvidenceStatus.UNKNOWN,
    }
    assert contract.candle_intervals == {CandleInterval.ONE_MINUTE, CandleInterval.ONE_DAY}
    assert contract.timestamp.meaning is TimestampMeaning.INTERVAL_OPEN
    assert contract.timestamp.format == "ISO8601"
    assert contract.timestamp.provenance is EvidenceStatus.DOCUMENTED
    assert contract.pagination.max_page_size == 200
    assert contract.pagination.request_cursor_field == "before"
    assert contract.pagination.before_is_inclusive
    assert contract.pagination.response_cursor_field == "nextBefore"
    assert contract.pagination.null_cursor_terminates
    assert contract.pagination.provenance is EvidenceStatus.DOCUMENTED
    assert contract.adjustment.default_adjusted
    assert contract.adjustment.applied_or_not_applied is EvidenceStatus.DOCUMENTED
    assert contract.adjustment.corporate_action_method_and_factors is EvidenceStatus.UNKNOWN
    assert contract.universe.current_status_filters == {"SCHEDULED", "ACTIVE", "DELISTED"}
    assert contract.universe.list_date is EvidenceStatus.DOCUMENTED
    assert contract.universe.delist_date is EvidenceStatus.DOCUMENTED
    assert contract.universe.historical_completeness is EvidenceStatus.UNKNOWN
    assert contract.session_completion.timezone == "Asia/Seoul"
    assert (
        contract.session_completion.current_previous_next_business_days is EvidenceStatus.DOCUMENTED
    )
    assert contract.session_completion.integrated_krx_nxt_sessions is EvidenceStatus.DOCUMENTED
    assert contract.session_completion.historical_calendar_completeness is EvidenceStatus.UNKNOWN
    assert contract.session_completion.daily_candle_completion is EvidenceStatus.UNKNOWN
    assert contract.session_completion.daily_session_scope is EvidenceStatus.UNKNOWN
    assert contract.retention is EvidenceStatus.UNKNOWN
    assert contract.data_rights.local_storage is EvidenceStatus.UNKNOWN
    assert contract.data_rights.derived_use is EvidenceStatus.UNKNOWN
    assert contract.data_rights.redistribution is EvidenceStatus.UNKNOWN
    assert {(item.group, item.documented_tps) for item in contract.rate_limits} == {
        ("MARKET_DATA_CHART", 20),
        ("STOCK_ALL", 1),
    }
    assert all(item.headers_are_authoritative for item in contract.rate_limits)
    assert all(item.provenance is EvidenceStatus.DOCUMENTED for item in contract.rate_limits)


@pytest.mark.parametrize("value", [naive_stamp(), naive_stamp(10)])
def test_naive_timestamps_fail_closed(value: datetime) -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        require_aware_timestamp(value)


def test_one_minute_bounds_require_known_interval_open_meaning() -> None:
    assert derive_one_minute_bounds(stamp(), TimestampMeaning.INTERVAL_OPEN) == (
        stamp(),
        stamp() + timedelta(minutes=1),
    )
    with pytest.raises(ValueError, match="timestamp meaning"):
        derive_one_minute_bounds(stamp(), TimestampMeaning.UNKNOWN)
    with pytest.raises(ValueError, match="timezone-aware"):
        derive_one_minute_bounds(naive_stamp(), TimestampMeaning.INTERVAL_OPEN)


def test_daily_completion_requires_an_explicit_valid_session_end() -> None:
    candle = seoul_stamp()
    session_end = seoul_stamp(15, 30)
    with pytest.raises(ValueError, match="explicit session end"):
        require_daily_session_end(
            candle,
            None,
            TimestampMeaning.INTERVAL_OPEN,
            session_timezone="Asia/Seoul",
        )
    with pytest.raises(ValueError, match="timestamp meaning"):
        require_daily_session_end(
            candle,
            session_end,
            TimestampMeaning.UNKNOWN,
            session_timezone="Asia/Seoul",
        )
    with pytest.raises(ValueError, match="after"):
        require_daily_session_end(
            candle,
            candle,
            TimestampMeaning.INTERVAL_OPEN,
            session_timezone="Asia/Seoul",
        )
    with pytest.raises(ValueError, match="timezone-aware"):
        require_daily_session_end(
            candle,
            naive_stamp(15, 30),
            TimestampMeaning.INTERVAL_OPEN,
            session_timezone="Asia/Seoul",
        )
    with pytest.raises(ValueError, match="IANA"):
        require_daily_session_end(
            candle,
            session_end,
            TimestampMeaning.INTERVAL_OPEN,
            session_timezone="not/a-timezone",
        )
    with pytest.raises(ValueError, match="provider-local"):
        require_daily_session_end(
            candle,
            datetime(2026, 8, 24, 15, 30, tzinfo=UTC),
            TimestampMeaning.INTERVAL_OPEN,
            session_timezone="Asia/Seoul",
        )
    assert require_daily_session_end(
        candle,
        session_end,
        TimestampMeaning.INTERVAL_OPEN,
        session_timezone="Asia/Seoul",
    ) == (
        candle,
        session_end,
    )


def test_daily_session_completion_requires_aware_observation_and_explicit_iana_timezone() -> None:
    session_end = seoul_stamp(15, 30)
    assert not is_daily_session_complete(
        seoul_stamp(15, 29), session_end, session_timezone="Asia/Seoul"
    )
    assert is_daily_session_complete(
        seoul_stamp(15, 30), session_end, session_timezone="Asia/Seoul"
    )
    with pytest.raises(ValueError, match="timezone-aware"):
        is_daily_session_complete(naive_stamp(15, 30), session_end, session_timezone="Asia/Seoul")
    with pytest.raises(ValueError, match="timezone-aware"):
        is_daily_session_complete(
            seoul_stamp(15, 30), naive_stamp(15, 30), session_timezone="Asia/Seoul"
        )
    with pytest.raises(ValueError, match="IANA"):
        is_daily_session_complete(seoul_stamp(15, 30), session_end, session_timezone="KST")


def test_page_order_is_strictly_descending_and_aware() -> None:
    validate_descending_page((stamp(9, 2), stamp(9, 1), stamp(9)))
    with pytest.raises(ValueError, match="strictly descending"):
        validate_descending_page((stamp(9), stamp(9)))
    with pytest.raises(ValueError, match="strictly descending"):
        validate_descending_page((stamp(9), stamp(9, 1)))
    with pytest.raises(ValueError, match="timezone-aware"):
        validate_descending_page((stamp(), naive_stamp(8, 59)))


def test_cursor_validation_rejects_repetition_and_non_monotone_progression() -> None:
    previous = (stamp(10),)
    validate_cursor_progression(stamp(9), stamp(8), previous)
    validate_cursor_progression(None, stamp(8), previous)
    with pytest.raises(ValueError, match="repeated"):
        validate_cursor_progression(stamp(10), stamp(9), previous)
    with pytest.raises(ValueError, match="repeated"):
        validate_cursor_progression(stamp(9), stamp(10), previous)
    with pytest.raises(ValueError, match="repeated"):
        validate_cursor_progression(stamp(9), stamp(9), previous)
    with pytest.raises(ValueError, match="move backward"):
        validate_cursor_progression(stamp(9), stamp(9, 1), previous)
    with pytest.raises(ValueError, match="timezone-aware"):
        validate_cursor_progression(naive_stamp(), None)


def test_cursor_need_not_equal_or_predate_oldest_bar() -> None:
    # The cursor is provider-controlled.  It may precede neither bar while still
    # progressing monotonically from the request cursor.
    validate_candle_page(
        (stamp(9, 2), stamp(9, 1)),
        requested_before=stamp(10),
        next_before=stamp(9, 59),
    )


def test_empty_candle_page_must_terminate() -> None:
    validate_candle_page((), requested_before=stamp(9), next_before=None)
    with pytest.raises(ValueError, match="must terminate"):
        validate_candle_page((), requested_before=stamp(9), next_before=stamp(8))


def test_individual_membership_requires_explicit_delist_semantics() -> None:
    listed = date(2026, 8, 24)
    delisted = date(2026, 8, 25)
    assert is_individually_listed_on(
        delisted,
        list_date=listed,
        delist_date=delisted,
        delist_boundary=DelistBoundary.INCLUSIVE,
    )
    assert not is_individually_listed_on(
        delisted,
        list_date=listed,
        delist_date=delisted,
        delist_boundary=DelistBoundary.EXCLUSIVE,
    )
    assert is_individually_listed_on(
        date(2026, 8, 26), list_date=listed, delist_date=None, delist_boundary=None
    )
    with pytest.raises(ValueError, match="semantics"):
        is_individually_listed_on(
            listed, list_date=listed, delist_date=delisted, delist_boundary=None
        )
    with pytest.raises(ValueError, match="requires a delist date"):
        is_individually_listed_on(
            listed,
            list_date=listed,
            delist_date=None,
            delist_boundary=DelistBoundary.INCLUSIVE,
        )
    with pytest.raises(ValueError, match="cannot precede"):
        is_individually_listed_on(
            listed,
            list_date=delisted,
            delist_date=listed,
            delist_boundary=DelistBoundary.INCLUSIVE,
        )
    with pytest.raises(TypeError, match="calendar date"):
        is_individually_listed_on(
            stamp(),
            list_date=listed,
            delist_date=None,
            delist_boundary=None,
        )


def test_safe_spacing_uses_current_header_tps_and_never_less_than_one_multiplier() -> None:
    assert safe_request_spacing_seconds(20) == pytest.approx(0.055)
    assert safe_request_spacing_seconds("20", safety_multiplier=1.5) == pytest.approx(0.075)
    stock_all = next(
        item for item in TOSS_KR_DATA_CONTRACT.rate_limits if item.group == "STOCK_ALL"
    )
    assert safe_request_spacing_seconds(stock_all.documented_tps) == pytest.approx(1.1)
    with pytest.raises(ValueError, match="positive integer"):
        safe_request_spacing_seconds(0)
    with pytest.raises(ValueError, match="positive integer"):
        safe_request_spacing_seconds("20.0")
    with pytest.raises(ValueError, match="at least"):
        safe_request_spacing_seconds(20, safety_multiplier=0.999)


def test_gate_e_blockers_are_stable_and_exclude_known_timestamp_and_pagination() -> None:
    assert gate_e_blockers() == (
        GateEBlocker.RETENTION_UNKNOWN,
        GateEBlocker.HISTORICAL_UNIVERSE_COMPLETENESS_UNKNOWN,
        GateEBlocker.CORPORATE_ACTION_METHOD_FACTORS_UNKNOWN,
        GateEBlocker.DAILY_COMPLETION_SESSION_SCOPE_UNKNOWN,
        GateEBlocker.MARKET_DATA_RIGHTS_UNKNOWN,
    )


def test_observed_only_evidence_does_not_unlock_gate_e() -> None:
    contract = replace(
        TOSS_KR_DATA_CONTRACT,
        timestamp=replace(
            TOSS_KR_DATA_CONTRACT.timestamp,
            provenance=EvidenceStatus.OBSERVED,
        ),
        pagination=replace(
            TOSS_KR_DATA_CONTRACT.pagination,
            provenance=EvidenceStatus.OBSERVED,
        ),
        retention=EvidenceStatus.OBSERVED,
        data_rights=replace(
            TOSS_KR_DATA_CONTRACT.data_rights,
            local_storage=EvidenceStatus.OBSERVED,
            derived_use=EvidenceStatus.OBSERVED,
            redistribution=EvidenceStatus.OBSERVED,
        ),
    )
    blockers = gate_e_blockers(contract)
    assert GateEBlocker.TIMESTAMP_SEMANTICS_UNDOCUMENTED in blockers
    assert GateEBlocker.PAGINATION_SEMANTICS_UNDOCUMENTED in blockers
    assert GateEBlocker.RETENTION_UNKNOWN in blockers
    assert GateEBlocker.MARKET_DATA_RIGHTS_UNKNOWN in blockers
