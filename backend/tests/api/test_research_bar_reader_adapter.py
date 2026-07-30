"""Research bar reader uses session-depth loads (Phase 55 / ADR-0056)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from aegis.api.dependencies import ResearchBarReaderAdapter


class _FakeRepo:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, int]] = []

    async def list_recent(self, symbol: str, limit: int) -> list[Any]:
        self.calls.append(("list_recent", symbol, limit))
        return []

    async def list_recent_for_sessions(self, symbol: str, session_limit: int) -> list[Any]:
        self.calls.append(("list_recent_for_sessions", symbol, session_limit))
        return [
            _FakeRow(
                trading_date=date(2024, 1, 26),
                source="alpha_vantage",
            ),
            _FakeRow(
                trading_date=date(2024, 1, 26),
                source="polygon",
            ),
            _FakeRow(
                trading_date=date(2024, 1, 25),
                source="polygon",
            ),
        ]


class _FakeRow:
    def __init__(self, *, trading_date: date, source: str) -> None:
        value = Decimal("100")
        self.trading_date = trading_date
        self.open = value
        self.high = value
        self.low = value
        self.close = value
        self.volume = 1
        self.data_quality = "primary"
        self.source = source


@pytest.mark.asyncio
async def test_research_bar_reader_uses_session_depth_load() -> None:
    repo = _FakeRepo()
    adapter = ResearchBarReaderAdapter(repo)  # type: ignore[arg-type]

    bars = await adapter.list_recent_bars("AAPL", 252)

    assert repo.calls == [("list_recent_for_sessions", "AAPL", 252)]
    assert len(bars) == 3
    assert {b.source for b in bars} == {"alpha_vantage", "polygon"}
    assert {b.trading_date for b in bars} == {date(2024, 1, 26), date(2024, 1, 25)}
