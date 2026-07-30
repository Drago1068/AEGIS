"""Service tests for configurable research bar load limit (Phase 51)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from aegis.domain.research_assessment import (
    ResearchAssessmentService,
    ResearchAssessmentUnavailableError,
    ResearchBarInput,
)


class _FakeBarReader:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    async def list_recent_bars(self, symbol: str, limit: int) -> list[ResearchBarInput]:
        self.calls.append((symbol, limit))
        # Too few bars: assess/backfill fail-closed without needing a full store.
        value = Decimal("100")
        return [
            ResearchBarInput(
                trading_date=date(2024, 1, 26),
                open=value,
                high=value,
                low=value,
                close=value,
                volume=1,
                source="alpha_vantage",
                data_quality="primary",
            )
        ]


class _FakeStore:
    async def insert(self, snapshot: Any) -> Any:
        raise AssertionError("must not insert")

    async def list_recent(self, symbol: str, limit: int) -> list[Any]:
        return []

    async def get_latest(self, symbol: str) -> None:
        return None


@pytest.mark.asyncio
async def test_assess_uses_configured_bar_load_limit() -> None:
    reader = _FakeBarReader()
    service = ResearchAssessmentService(
        reader,
        _FakeStore(),
        calendar_name="NYSE",
        max_latest_bar_staleness_trading_days=5,
        bar_load_limit=252,
    )
    with pytest.raises(ResearchAssessmentUnavailableError):
        await service.assess("AAPL")
    assert reader.calls == [("AAPL", 252)]


@pytest.mark.asyncio
async def test_backfill_assessments_uses_configured_bar_load_limit() -> None:
    reader = _FakeBarReader()
    store = _FakeStore()
    service = ResearchAssessmentService(
        reader,
        store,
        calendar_name="NYSE",
        max_latest_bar_staleness_trading_days=5,
        bar_load_limit=180,
    )
    summary = await service.backfill_assessments("AAPL", limit=5)
    assert reader.calls == [("AAPL", 180)]
    assert summary.candidate_count == 0
