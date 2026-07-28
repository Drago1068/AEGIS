"""Daily-bar rejection rules per ``docs/architecture/market-data-contracts.md``.

Adapted for daily-bar granularity per ADR-0002: there is no intraday open/closed state to
check, so "closed-session" means the bar's trading date is not a real exchange session day,
and "stale" is evaluated only against the most recent bar in an ingestion run (see
``is_latest_bar`` below), never against an intentionally old backfill bar.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum

from aegis.domain.calendars import is_trading_day, most_recent_trading_day
from aegis.providers.market_data import DailyBar


class RejectionReason(StrEnum):
    """Why a raw daily bar was rejected. Never persisted as a valid observation."""

    INVALID = "invalid"
    NON_POSITIVE = "non_positive"
    CLOSED_SESSION = "closed_session"
    STALE = "stale"
    UNUSABLE = "unusable"


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """The outcome of validating a single :class:`~aegis.providers.market_data.DailyBar`."""

    is_valid: bool
    reason: RejectionReason | None = None
    detail: str | None = None

    @staticmethod
    def accepted() -> ValidationResult:
        return ValidationResult(is_valid=True)

    @staticmethod
    def rejected(reason: RejectionReason, detail: str) -> ValidationResult:
        return ValidationResult(is_valid=False, reason=reason, detail=detail)


def validate_daily_bar(
    bar: DailyBar,
    *,
    calendar_name: str,
    as_of: date,
    max_staleness_trading_days: int,
    is_latest_bar: bool,
) -> ValidationResult:
    """Validate one raw daily bar against every rejection rule.

    Args:
        bar: the raw bar to validate.
        calendar_name: exchange calendar identity (configuration, not hardcoded).
        as_of: the date the ingestion run is considered to be running as of (normally today,
            injectable for deterministic tests).
        max_staleness_trading_days: see
            ``Settings.max_latest_bar_staleness_trading_days``.
        is_latest_bar: whether ``bar`` is the most recent bar returned for its symbol in this
            run. Staleness is only evaluated for this bar; older bars in the same backfill are
            expected to be "old" and are not rejected for it.
    """

    positivity_result = _validate_positive(bar)
    if positivity_result is not None:
        return positivity_result

    consistency_result = _validate_ohlc_consistency(bar)
    if consistency_result is not None:
        return consistency_result

    if not is_trading_day(bar.trading_date, calendar_name):
        return ValidationResult.rejected(
            RejectionReason.CLOSED_SESSION,
            f"{bar.trading_date.isoformat()} is not a {calendar_name} trading day",
        )

    if is_latest_bar:
        staleness_result = _validate_staleness(
            bar, calendar_name=calendar_name, as_of=as_of,
            max_staleness_trading_days=max_staleness_trading_days,
        )
        if staleness_result is not None:
            return staleness_result

    return ValidationResult.accepted()


def _validate_ohlc_consistency(bar: DailyBar) -> ValidationResult | None:
    """Reject internally-inconsistent OHLC values (a malformed/corrupt provider record).

    ``high`` must be the maximum and ``low`` the minimum of open/high/low/close; any other
    relationship cannot represent a real trading session and indicates a shape/parsing defect
    upstream that slipped past the provider adapter.
    """

    if bar.high < bar.low:
        return ValidationResult.rejected(
            RejectionReason.INVALID, f"high={bar.high} is less than low={bar.low}"
        )
    if bar.high < bar.open or bar.high < bar.close:
        return ValidationResult.rejected(
            RejectionReason.INVALID,
            f"high={bar.high} is less than open={bar.open} or close={bar.close}",
        )
    if bar.low > bar.open or bar.low > bar.close:
        return ValidationResult.rejected(
            RejectionReason.INVALID,
            f"low={bar.low} is greater than open={bar.open} or close={bar.close}",
        )
    return None


def _validate_positive(bar: DailyBar) -> ValidationResult | None:
    for field_name, value in (
        ("open", bar.open),
        ("high", bar.high),
        ("low", bar.low),
        ("close", bar.close),
    ):
        if value <= 0:
            return ValidationResult.rejected(
                RejectionReason.NON_POSITIVE, f"{field_name}={value} is not positive"
            )
    if bar.volume < 0:
        return ValidationResult.rejected(
            RejectionReason.NON_POSITIVE, f"volume={bar.volume} is negative"
        )
    return None


def _validate_staleness(
    bar: DailyBar,
    *,
    calendar_name: str,
    as_of: date,
    max_staleness_trading_days: int,
) -> ValidationResult | None:
    latest_expected = most_recent_trading_day(as_of, calendar_name)
    if bar.trading_date >= latest_expected:
        return None

    lag_trading_days = _count_trading_days_strictly_between(
        bar.trading_date, latest_expected, calendar_name
    )
    if lag_trading_days > max_staleness_trading_days:
        return ValidationResult.rejected(
            RejectionReason.STALE,
            (
                f"latest bar dated {bar.trading_date.isoformat()} is {lag_trading_days} "
                f"trading day(s) behind the expected latest session "
                f"{latest_expected.isoformat()}"
            ),
        )
    return None


def _count_trading_days_strictly_between(
    start: date, end: date, calendar_name: str
) -> int:
    """Count trading days strictly after ``start`` and up to and including ``end``."""

    count = 0
    current = start
    while current < end:
        current += timedelta(days=1)
        if is_trading_day(current, calendar_name):
            count += 1
    return count
