"""Unit tests for Phase 6 / Phase 11 research-only assessment domain logic."""

from __future__ import annotations

import math
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from aegis.domain.research_assessment import (
    LOOKBACK_SESSIONS,
    METHOD_ID,
    METHOD_VERSION_V1,
    METHOD_VERSION_V2,
    MULTI_SOURCE_AGREEMENT_FLOOR,
    SCHEMA_VERSION_V1,
    SCHEMA_VERSION_V2,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentReason,
    ResearchAssessmentUnavailableError,
    ResearchBarInput,
    ResearchMultiSourceCoverageConfig,
    assess_from_bars,
    compute_coverage_confidence,
    compute_realized_vol_20,
    compute_research_index,
    compute_total_return_20,
    is_usable_ohlcv,
)

_CALENDAR = "NYSE"
# Fixed as_of: Friday 2024-01-26; expected latest NYSE session is that day.
_AS_OF = date(2024, 1, 26)
_COMPUTED_AT = datetime(2024, 1, 26, 18, 0, tzinfo=UTC)


def _closes_to_bars(
    closes: list[Decimal],
    *,
    end_date: date = date(2024, 1, 26),
    data_quality: str = "primary",
    source: str = "alpha_vantage",
) -> list[ResearchBarInput]:
    """Build chronological primary bars ending on ``end_date`` (must be a session day)."""

    from aegis.domain.calendars import is_trading_day

    session_dates: list[date] = []
    cursor = end_date
    while len(session_dates) < len(closes):
        if is_trading_day(cursor, _CALENDAR):
            session_dates.append(cursor)
        cursor = date.fromordinal(cursor.toordinal() - 1)
    session_dates.reverse()

    bars: list[ResearchBarInput] = []
    for trading_date, close in zip(session_dates, closes, strict=True):
        bars.append(
            ResearchBarInput(
                trading_date=trading_date,
                open=close,
                high=close,
                low=close,
                close=close,
                volume=1_000,
                data_quality=data_quality,
                source=source,
            )
        )
    return bars


def _twenty_rising_closes() -> list[Decimal]:
    return [Decimal(100 + i) for i in range(LOOKBACK_SESSIONS)]


def _multi_source_config(**overrides: object) -> ResearchMultiSourceCoverageConfig:
    defaults: dict[str, object] = {
        "enabled": True,
        "primary_source": "alpha_vantage",
        "secondary_source": "polygon",
        "close_tolerance": 0.002,
        "disagreement_fail_closed": False,
        "allow_cross_source_component_fill": False,
    }
    defaults.update(overrides)
    return ResearchMultiSourceCoverageConfig(**defaults)  # type: ignore[arg-type]


def test_is_usable_ohlcv_rejects_non_positive_close() -> None:
    bar = ResearchBarInput(
        trading_date=date(2024, 1, 2),
        open=Decimal("1"),
        high=Decimal("1"),
        low=Decimal("1"),
        close=Decimal("0"),
        volume=1,
        data_quality="primary",
        source="alpha_vantage",
    )
    assert not is_usable_ohlcv(bar)


def test_total_return_20_matches_fixture() -> None:
    closes = _twenty_rising_closes()
    # (119 / 100) - 1 = 0.19
    assert compute_total_return_20(closes) == pytest.approx(0.19)


def test_realized_vol_20_and_research_index_fixtures() -> None:
    closes = _twenty_rising_closes()
    vol = compute_realized_vol_20(closes)
    total_return = compute_total_return_20(closes)
    index = compute_research_index(total_return, vol)

    log_returns = [
        math.log(float(closes[i] / closes[i - 1])) for i in range(1, len(closes))
    ]
    import statistics

    expected_vol = statistics.stdev(log_returns) * math.sqrt(252)
    assert vol == pytest.approx(expected_vol)
    assert index == pytest.approx(math.tanh(total_return / max(vol, 1e-12)))
    assert -1.0 <= index <= 1.0


def test_coverage_confidence_product_formula() -> None:
    # Latest bar on as_of => freshness 1; 20/20 primary in a 20-bar window => 1 * 1 * 1
    coverage = compute_coverage_confidence(
        usable_primary_bars=20,
        total_bars_in_lookback_window=20,
        latest_trading_date=_AS_OF,
        calendar_name=_CALENDAR,
        as_of=_AS_OF,
        max_staleness_trading_days=3,
    )
    assert coverage == pytest.approx(1.0)

    # 20 primary of 25 bars in window => primary_fraction 0.8
    coverage_mixed = compute_coverage_confidence(
        usable_primary_bars=20,
        total_bars_in_lookback_window=25,
        latest_trading_date=_AS_OF,
        calendar_name=_CALENDAR,
        as_of=_AS_OF,
        max_staleness_trading_days=3,
    )
    assert coverage_mixed == pytest.approx(0.8)

    # One trading day behind 2024-01-26 is 2024-01-25; lag=1, freshness=1-1/4=0.75
    coverage_lag = compute_coverage_confidence(
        usable_primary_bars=20,
        total_bars_in_lookback_window=20,
        latest_trading_date=date(2024, 1, 25),
        calendar_name=_CALENDAR,
        as_of=_AS_OF,
        max_staleness_trading_days=3,
    )
    assert coverage_lag == pytest.approx(0.75)


def test_coverage_confidence_includes_multi_source_factors() -> None:
    coverage = compute_coverage_confidence(
        usable_primary_bars=20,
        total_bars_in_lookback_window=20,
        latest_trading_date=_AS_OF,
        calendar_name=_CALENDAR,
        as_of=_AS_OF,
        max_staleness_trading_days=3,
        source_availability_factor=0.5,
        source_agreement_factor=0.8,
    )
    assert coverage == pytest.approx(0.4)


def test_assess_from_bars_success_is_research_only() -> None:
    bars = _closes_to_bars(_twenty_rising_closes())
    # API/readers supply newest-first
    newest_first = list(reversed(bars))
    snapshot = assess_from_bars(
        "aapl",
        newest_first,
        calendar_name=_CALENDAR,
        max_latest_bar_staleness_trading_days=3,
        as_of=_AS_OF,
        computed_at=_COMPUTED_AT,
    )

    assert snapshot.symbol == "AAPL"
    assert snapshot.method_id == METHOD_ID
    assert snapshot.method_version == METHOD_VERSION_V1
    assert snapshot.schema_version == SCHEMA_VERSION_V1
    assert snapshot.state == STATE_RESEARCH_ONLY
    assert snapshot.probability_confidence is None
    assert 0.0 <= snapshot.coverage_confidence <= 1.0
    assert snapshot.bar_count == LOOKBACK_SESSIONS
    assert "total_return_20" in snapshot.components
    assert "realized_vol_20" in snapshot.components
    assert "research_index" in snapshot.components


def test_assess_fails_closed_on_insufficient_primary_bars() -> None:
    bars = _closes_to_bars(_twenty_rising_closes()[:10])
    with pytest.raises(ResearchAssessmentUnavailableError) as exc_info:
        assess_from_bars(
            "AAPL",
            list(reversed(bars)),
            calendar_name=_CALENDAR,
            max_latest_bar_staleness_trading_days=3,
            as_of=_AS_OF,
            computed_at=_COMPUTED_AT,
        )
    assert exc_info.value.reason is ResearchAssessmentReason.INSUFFICIENT_PRIMARY_BARS


def test_assess_fails_closed_on_unusable_ohlcv() -> None:
    bars = _closes_to_bars(_twenty_rising_closes())
    bad = bars[-1]
    bars[-1] = ResearchBarInput(
        trading_date=bad.trading_date,
        open=Decimal("100"),
        high=Decimal("90"),
        low=Decimal("95"),
        close=Decimal("100"),
        volume=1,
        data_quality="primary",
        source="alpha_vantage",
    )
    with pytest.raises(ResearchAssessmentUnavailableError) as exc_info:
        assess_from_bars(
            "AAPL",
            list(reversed(bars)),
            calendar_name=_CALENDAR,
            max_latest_bar_staleness_trading_days=3,
            as_of=_AS_OF,
            computed_at=_COMPUTED_AT,
        )
    assert exc_info.value.reason is ResearchAssessmentReason.UNUSABLE_OHLCV


def test_assess_fails_closed_on_stale_latest_bar() -> None:
    # End window far before as_of so latest is stale beyond max_staleness=3
    bars = _closes_to_bars(
        _twenty_rising_closes(), end_date=date(2024, 1, 12)
    )
    with pytest.raises(ResearchAssessmentUnavailableError) as exc_info:
        assess_from_bars(
            "AAPL",
            list(reversed(bars)),
            calendar_name=_CALENDAR,
            max_latest_bar_staleness_trading_days=3,
            as_of=_AS_OF,
            computed_at=_COMPUTED_AT,
        )
    assert exc_info.value.reason is ResearchAssessmentReason.STALE_LATEST_BAR


def test_multi_source_disabled_preserves_v1() -> None:
    bars = _closes_to_bars(_twenty_rising_closes())
    snapshot = assess_from_bars(
        "AAPL",
        list(reversed(bars)),
        calendar_name=_CALENDAR,
        max_latest_bar_staleness_trading_days=3,
        as_of=_AS_OF,
        computed_at=_COMPUTED_AT,
        multi_source=_multi_source_config(enabled=False),
    )
    assert snapshot.method_version == METHOD_VERSION_V1
    assert snapshot.schema_version == SCHEMA_VERSION_V1
    assert "source_agreement_factor" not in snapshot.components


def test_multi_source_single_source_agreement_is_one() -> None:
    """comparable_dates==0 must not tank agreement (single-source install)."""

    bars = _closes_to_bars(_twenty_rising_closes(), source="alpha_vantage")
    snapshot = assess_from_bars(
        "AAPL",
        list(reversed(bars)),
        calendar_name=_CALENDAR,
        max_latest_bar_staleness_trading_days=3,
        as_of=_AS_OF,
        computed_at=_COMPUTED_AT,
        multi_source=_multi_source_config(secondary_source=None),
    )
    assert snapshot.method_version == METHOD_VERSION_V2
    assert snapshot.schema_version == SCHEMA_VERSION_V2
    assert snapshot.probability_confidence is None
    assert snapshot.state == STATE_RESEARCH_ONLY
    assert snapshot.components["source_agreement_factor"] == pytest.approx(1.0)
    assert snapshot.components["comparable_dates"] == 0
    assert snapshot.components["component_source"] == "alpha_vantage"
    assert snapshot.coverage_confidence == pytest.approx(1.0)


def test_multi_source_agreeing_closes_keep_high_coverage() -> None:
    primary = _closes_to_bars(_twenty_rising_closes(), source="alpha_vantage")
    # Secondary closes within 0.1% of primary (OHLC kept consistent).
    secondary = [
        ResearchBarInput(
            trading_date=bar.trading_date,
            open=bar.close * Decimal("1.001"),
            high=bar.close * Decimal("1.001"),
            low=bar.close * Decimal("1.001"),
            close=bar.close * Decimal("1.001"),
            volume=bar.volume,
            data_quality="primary",
            source="polygon",
        )
        for bar in primary
    ]
    combined = list(reversed(primary + secondary))
    snapshot = assess_from_bars(
        "AAPL",
        combined,
        calendar_name=_CALENDAR,
        max_latest_bar_staleness_trading_days=3,
        as_of=_AS_OF,
        computed_at=_COMPUTED_AT,
        multi_source=_multi_source_config(),
    )
    assert snapshot.method_version == METHOD_VERSION_V2
    assert snapshot.components["comparable_dates"] == LOOKBACK_SESSIONS
    assert snapshot.components["agreeing_dates"] == LOOKBACK_SESSIONS
    assert snapshot.components["source_agreement_factor"] == pytest.approx(1.0)
    assert snapshot.components["component_source"] == "alpha_vantage"
    # Components use primary closes only (no blend).
    assert snapshot.components["total_return_20"] == pytest.approx(0.19)


def test_multi_source_disagreement_soft_penalty() -> None:
    primary = _closes_to_bars(_twenty_rising_closes(), source="alpha_vantage")
    secondary = [
        ResearchBarInput(
            trading_date=bar.trading_date,
            open=bar.close * Decimal("1.05"),
            high=bar.close * Decimal("1.05"),
            low=bar.close * Decimal("1.05"),
            close=bar.close * Decimal("1.05"),  # 5% off >> 0.2% tolerance
            volume=bar.volume,
            data_quality="primary",
            source="polygon",
        )
        for bar in primary
    ]
    snapshot = assess_from_bars(
        "AAPL",
        list(reversed(primary + secondary)),
        calendar_name=_CALENDAR,
        max_latest_bar_staleness_trading_days=3,
        as_of=_AS_OF,
        computed_at=_COMPUTED_AT,
        multi_source=_multi_source_config(disagreement_fail_closed=False),
    )
    assert snapshot.components["source_agreement_factor"] == pytest.approx(0.0)
    assert snapshot.coverage_confidence == pytest.approx(0.0)


def test_multi_source_disagreement_fail_closed() -> None:
    primary = _closes_to_bars(_twenty_rising_closes(), source="alpha_vantage")
    secondary = [
        ResearchBarInput(
            trading_date=bar.trading_date,
            open=bar.close * Decimal("1.05"),
            high=bar.close * Decimal("1.05"),
            low=bar.close * Decimal("1.05"),
            close=bar.close * Decimal("1.05"),
            volume=bar.volume,
            data_quality="primary",
            source="polygon",
        )
        for bar in primary
    ]
    with pytest.raises(ResearchAssessmentUnavailableError) as exc_info:
        assess_from_bars(
            "AAPL",
            list(reversed(primary + secondary)),
            calendar_name=_CALENDAR,
            max_latest_bar_staleness_trading_days=3,
            as_of=_AS_OF,
            computed_at=_COMPUTED_AT,
            multi_source=_multi_source_config(disagreement_fail_closed=True),
        )
    assert exc_info.value.reason is ResearchAssessmentReason.MULTI_SOURCE_DISAGREEMENT
    assert pytest.approx(0.80) == MULTI_SOURCE_AGREEMENT_FLOOR


def test_multi_source_prefers_primary_rejects_secondary_only_without_fill() -> None:
    secondary_only = _closes_to_bars(_twenty_rising_closes(), source="polygon")
    with pytest.raises(ResearchAssessmentUnavailableError) as exc_info:
        assess_from_bars(
            "AAPL",
            list(reversed(secondary_only)),
            calendar_name=_CALENDAR,
            max_latest_bar_staleness_trading_days=3,
            as_of=_AS_OF,
            computed_at=_COMPUTED_AT,
            multi_source=_multi_source_config(allow_cross_source_component_fill=False),
        )
    assert exc_info.value.reason is ResearchAssessmentReason.INSUFFICIENT_PRIMARY_BARS


def test_multi_source_cross_source_fill_when_enabled() -> None:
    primary_partial = _closes_to_bars(
        _twenty_rising_closes()[:10], source="alpha_vantage"
    )
    # Secondary covers full 20 sessions; fill uses secondary for missing primary dates.
    secondary_full = _closes_to_bars(_twenty_rising_closes(), source="polygon")
    snapshot = assess_from_bars(
        "AAPL",
        list(reversed(primary_partial + secondary_full)),
        calendar_name=_CALENDAR,
        max_latest_bar_staleness_trading_days=3,
        as_of=_AS_OF,
        computed_at=_COMPUTED_AT,
        multi_source=_multi_source_config(allow_cross_source_component_fill=True),
    )
    assert snapshot.method_version == METHOD_VERSION_V2
    assert snapshot.components["component_source"] == "mixed"
    assert snapshot.probability_confidence is None
