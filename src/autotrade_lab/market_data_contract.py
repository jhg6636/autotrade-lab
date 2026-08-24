"""Provider-neutral, fail-closed market-data contract primitives.

This module records what a provider documents; it deliberately does not turn an
undocumented property into an assumption.  It contains no HTTP client code.
"""

from __future__ import annotations

from collections.abc import Collection, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from itertools import pairwise
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class EvidenceStatus(str, Enum):
    """Whether a fact is documented, locally observed, or still unknown."""

    DOCUMENTED = "documented"
    OBSERVED = "observed"
    UNKNOWN = "unknown"


class TimestampMeaning(str, Enum):
    UNKNOWN = "unknown"
    INTERVAL_OPEN = "interval_open"


class CandleInterval(str, Enum):
    ONE_MINUTE = "1m"
    ONE_DAY = "1d"


class DelistBoundary(str, Enum):
    """Whether the recorded delist date remains a listed date."""

    INCLUSIVE = "inclusive"
    EXCLUSIVE = "exclusive"


class GateEBlocker(str, Enum):
    TIMESTAMP_SEMANTICS_UNDOCUMENTED = "timestamp_semantics_undocumented"
    PAGINATION_SEMANTICS_UNDOCUMENTED = "pagination_semantics_undocumented"
    RETENTION_UNKNOWN = "retention_unknown"
    HISTORICAL_UNIVERSE_COMPLETENESS_UNKNOWN = "historical_universe_completeness_unknown"
    CORPORATE_ACTION_METHOD_FACTORS_UNKNOWN = "corporate_action_method_factors_unknown"
    DAILY_COMPLETION_SESSION_SCOPE_UNKNOWN = "daily_completion_session_scope_unknown"
    MARKET_DATA_RIGHTS_UNKNOWN = "market_data_rights_unknown"


@dataclass(frozen=True, slots=True)
class TimestampContract:
    meaning: TimestampMeaning
    format: str
    provenance: EvidenceStatus


@dataclass(frozen=True, slots=True)
class PaginationContract:
    max_page_size: int
    request_cursor_field: str
    before_is_inclusive: bool
    response_cursor_field: str
    null_cursor_terminates: bool
    provenance: EvidenceStatus


@dataclass(frozen=True, slots=True)
class AdjustmentContract:
    default_adjusted: bool
    applied_or_not_applied: EvidenceStatus
    corporate_action_method_and_factors: EvidenceStatus


@dataclass(frozen=True, slots=True)
class UniverseContract:
    current_status_filters: frozenset[str]
    list_date: EvidenceStatus
    delist_date: EvidenceStatus
    historical_completeness: EvidenceStatus


@dataclass(frozen=True, slots=True)
class RateLimitContract:
    group: str
    documented_tps: int
    headers_are_authoritative: bool
    provenance: EvidenceStatus


@dataclass(frozen=True, slots=True)
class DataRightsContract:
    local_storage: EvidenceStatus
    derived_use: EvidenceStatus
    redistribution: EvidenceStatus


@dataclass(frozen=True, slots=True)
class SessionCompletionContract:
    timezone: str
    current_previous_next_business_days: EvidenceStatus
    integrated_krx_nxt_sessions: EvidenceStatus
    historical_calendar_completeness: EvidenceStatus
    daily_candle_completion: EvidenceStatus
    daily_session_scope: EvidenceStatus


@dataclass(frozen=True, slots=True)
class ProviderDataContract:
    provider: str
    candle_intervals: frozenset[CandleInterval]
    timestamp: TimestampContract
    pagination: PaginationContract
    adjustment: AdjustmentContract
    universe: UniverseContract
    rate_limits: tuple[RateLimitContract, ...]
    session_completion: SessionCompletionContract
    retention: EvidenceStatus
    data_rights: DataRightsContract


TOSS_KR_DATA_CONTRACT = ProviderDataContract(
    provider="toss_kr",
    candle_intervals=frozenset((CandleInterval.ONE_MINUTE, CandleInterval.ONE_DAY)),
    timestamp=TimestampContract(
        meaning=TimestampMeaning.INTERVAL_OPEN,
        format="ISO8601",
        provenance=EvidenceStatus.DOCUMENTED,
    ),
    pagination=PaginationContract(
        max_page_size=200,
        request_cursor_field="before",
        before_is_inclusive=True,
        response_cursor_field="nextBefore",
        null_cursor_terminates=True,
        provenance=EvidenceStatus.DOCUMENTED,
    ),
    adjustment=AdjustmentContract(
        default_adjusted=True,
        applied_or_not_applied=EvidenceStatus.DOCUMENTED,
        corporate_action_method_and_factors=EvidenceStatus.UNKNOWN,
    ),
    universe=UniverseContract(
        current_status_filters=frozenset(("SCHEDULED", "ACTIVE", "DELISTED")),
        list_date=EvidenceStatus.DOCUMENTED,
        delist_date=EvidenceStatus.DOCUMENTED,
        historical_completeness=EvidenceStatus.UNKNOWN,
    ),
    rate_limits=(
        RateLimitContract(
            "MARKET_DATA_CHART",
            documented_tps=20,
            headers_are_authoritative=True,
            provenance=EvidenceStatus.DOCUMENTED,
        ),
        RateLimitContract(
            "STOCK_ALL",
            documented_tps=1,
            headers_are_authoritative=True,
            provenance=EvidenceStatus.DOCUMENTED,
        ),
    ),
    session_completion=SessionCompletionContract(
        timezone="Asia/Seoul",
        current_previous_next_business_days=EvidenceStatus.DOCUMENTED,
        integrated_krx_nxt_sessions=EvidenceStatus.DOCUMENTED,
        historical_calendar_completeness=EvidenceStatus.UNKNOWN,
        daily_candle_completion=EvidenceStatus.UNKNOWN,
        daily_session_scope=EvidenceStatus.UNKNOWN,
    ),
    retention=EvidenceStatus.UNKNOWN,
    data_rights=DataRightsContract(
        local_storage=EvidenceStatus.UNKNOWN,
        derived_use=EvidenceStatus.UNKNOWN,
        redistribution=EvidenceStatus.UNKNOWN,
    ),
)


def require_aware_timestamp(timestamp: datetime) -> datetime:
    """Return an aware timestamp or reject it before any temporal inference."""

    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return timestamp


def derive_one_minute_bounds(
    timestamp: datetime,
    meaning: TimestampMeaning,
) -> tuple[datetime, datetime]:
    """Return [open, close) only for a documented interval-open one-minute candle."""

    require_aware_timestamp(timestamp)
    if meaning is not TimestampMeaning.INTERVAL_OPEN:
        raise ValueError("cannot derive candle bounds when timestamp meaning is unknown")
    return timestamp, timestamp + timedelta(minutes=1)


def require_daily_session_end(
    candle_timestamp: datetime,
    session_end: datetime | None,
    meaning: TimestampMeaning,
    *,
    session_timezone: str,
) -> tuple[datetime, datetime]:
    """Return daily bounds only when the provider/session supplies an explicit end."""

    require_aware_timestamp(candle_timestamp)
    if meaning is not TimestampMeaning.INTERVAL_OPEN:
        raise ValueError("cannot derive daily bounds when timestamp meaning is unknown")
    if session_end is None:
        raise ValueError("daily completion requires an explicit session end")
    require_aware_timestamp(session_end)
    if session_end <= candle_timestamp:
        raise ValueError("session end must be after the daily candle timestamp")
    timezone = _require_iana_timezone(session_timezone)
    if candle_timestamp.astimezone(timezone).date() != session_end.astimezone(timezone).date():
        raise ValueError("session end must share the provider-local candle date")
    return candle_timestamp, session_end


def is_daily_session_complete(
    observed_at: datetime,
    session_end: datetime,
    *,
    session_timezone: str,
) -> bool:
    """Decide completion from an observed instant and an explicit session close."""

    require_aware_timestamp(observed_at)
    require_aware_timestamp(session_end)
    _require_iana_timezone(session_timezone)
    return observed_at >= session_end


def _require_iana_timezone(name: str) -> ZoneInfo:
    if not isinstance(name, str) or not name:
        raise ValueError("an explicit IANA session timezone is required")
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as error:
        raise ValueError("an explicit IANA session timezone is required") from error


def validate_descending_page(timestamps: Sequence[datetime]) -> None:
    """Require strictly descending, aware candle timestamps within one page."""

    for timestamp in timestamps:
        require_aware_timestamp(timestamp)
    if any(later >= earlier for earlier, later in pairwise(timestamps)):
        raise ValueError("candle page timestamps must be strictly descending")


def validate_cursor_progression(
    requested_before: datetime | None,
    next_before: datetime | None,
    previous_cursors: Collection[datetime] = (),
) -> None:
    """Reject repeated/non-monotone cursors without relating a cursor to page bars.

    ``previous_cursors`` means cursors used before ``requested_before``.  This
    intentionally does not compare ``next_before`` with the oldest candle: the
    provider documents cursor pass-through, not that relationship.
    """

    for cursor in previous_cursors:
        require_aware_timestamp(cursor)
    if requested_before is not None:
        require_aware_timestamp(requested_before)
        if requested_before in previous_cursors:
            raise ValueError("pagination cursor was repeated")
    if next_before is None:
        return
    require_aware_timestamp(next_before)
    if next_before in previous_cursors or next_before == requested_before:
        raise ValueError("pagination cursor was repeated")
    if requested_before is not None and next_before >= requested_before:
        raise ValueError("pagination cursor must move backward")


def validate_candle_page(
    timestamps: Sequence[datetime],
    *,
    requested_before: datetime | None,
    next_before: datetime | None,
    previous_cursors: Collection[datetime] = (),
) -> None:
    """Validate page order and cursor-chain safety without interpreting bar overlap."""

    validate_descending_page(timestamps)
    validate_cursor_progression(requested_before, next_before, previous_cursors)
    if not timestamps and next_before is not None:
        raise ValueError("an empty candle page must terminate pagination")


def is_individually_listed_on(
    as_of: date,
    *,
    list_date: date,
    delist_date: date | None,
    delist_boundary: DelistBoundary | None,
) -> bool:
    """Evaluate one instrument only; this never establishes universe completeness."""

    _require_calendar_date(as_of, "as_of")
    _require_calendar_date(list_date, "list_date")
    if delist_date is None:
        if delist_boundary is not None:
            raise ValueError("delist boundary requires a delist date")
        return as_of >= list_date
    _require_calendar_date(delist_date, "delist_date")
    if delist_boundary is None:
        raise ValueError("delist boundary semantics must be explicit")
    if delist_date < list_date:
        raise ValueError("delist date cannot precede list date")
    if delist_boundary is DelistBoundary.INCLUSIVE:
        return list_date <= as_of <= delist_date
    return list_date <= as_of < delist_date


def _require_calendar_date(value: date, name: str) -> None:
    if isinstance(value, datetime) or not isinstance(value, date):
        raise TypeError(f"{name} must be a calendar date, not a timestamp")


def safe_request_spacing_seconds(header_tps: int | str, *, safety_multiplier: float = 1.1) -> float:
    """Return a conservative spacing based on the currently observed TPS header."""

    try:
        tps = int(header_tps)
    except (TypeError, ValueError) as error:
        raise ValueError("header TPS must be a positive integer") from error
    if tps <= 0 or str(tps) != str(header_tps).strip():
        raise ValueError("header TPS must be a positive integer")
    if safety_multiplier < 1.0:
        raise ValueError("safety multiplier must be at least 1.0")
    return safety_multiplier / tps


def gate_e_blockers(
    contract: ProviderDataContract = TOSS_KR_DATA_CONTRACT,
) -> tuple[GateEBlocker, ...]:
    """Return stable blockers for claims that remain unsupported by this contract."""

    blockers: list[GateEBlocker] = []
    if (
        contract.timestamp.meaning is TimestampMeaning.UNKNOWN
        or contract.timestamp.provenance is not EvidenceStatus.DOCUMENTED
    ):
        blockers.append(GateEBlocker.TIMESTAMP_SEMANTICS_UNDOCUMENTED)
    if contract.pagination.provenance is not EvidenceStatus.DOCUMENTED:
        blockers.append(GateEBlocker.PAGINATION_SEMANTICS_UNDOCUMENTED)
    if contract.retention is not EvidenceStatus.DOCUMENTED:
        blockers.append(GateEBlocker.RETENTION_UNKNOWN)
    if contract.universe.historical_completeness is not EvidenceStatus.DOCUMENTED:
        blockers.append(GateEBlocker.HISTORICAL_UNIVERSE_COMPLETENESS_UNKNOWN)
    if contract.adjustment.corporate_action_method_and_factors is not EvidenceStatus.DOCUMENTED:
        blockers.append(GateEBlocker.CORPORATE_ACTION_METHOD_FACTORS_UNKNOWN)
    session = contract.session_completion
    if (
        session.daily_candle_completion is not EvidenceStatus.DOCUMENTED
        or session.daily_session_scope is not EvidenceStatus.DOCUMENTED
    ):
        blockers.append(GateEBlocker.DAILY_COMPLETION_SESSION_SCOPE_UNKNOWN)
    rights = contract.data_rights
    if any(
        status is not EvidenceStatus.DOCUMENTED
        for status in (rights.local_storage, rights.derived_use, rights.redistribution)
    ):
        blockers.append(GateEBlocker.MARKET_DATA_RIGHTS_UNKNOWN)
    return tuple(blockers)


__all__ = [
    "TOSS_KR_DATA_CONTRACT",
    "AdjustmentContract",
    "CandleInterval",
    "DataRightsContract",
    "DelistBoundary",
    "EvidenceStatus",
    "GateEBlocker",
    "PaginationContract",
    "ProviderDataContract",
    "RateLimitContract",
    "SessionCompletionContract",
    "TimestampContract",
    "TimestampMeaning",
    "UniverseContract",
    "derive_one_minute_bounds",
    "gate_e_blockers",
    "is_daily_session_complete",
    "is_individually_listed_on",
    "require_aware_timestamp",
    "require_daily_session_end",
    "safe_request_spacing_seconds",
    "validate_candle_page",
    "validate_cursor_progression",
    "validate_descending_page",
]
