"""Market data ingestion orchestration.

Depends only on :class:`~aegis.providers.market_data.DailyBarProvider` and the
:class:`DailyBarRepository` protocol defined below, per the domain/persistence module boundary
in ``docs/architecture/overview.md``: no FastAPI or SQLAlchemy import belongs in this module.
The concrete repository (``aegis.persistence.repositories.market_data``) satisfies this
protocol structurally without either module importing the other.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Protocol

from aegis.domain.market_data_validation import RejectionReason, validate_daily_bar
from aegis.providers.errors import ProviderError
from aegis.providers.market_data import DailyBar, DailyBarProvider

logger = logging.getLogger(__name__)


class DailyBarRepository(Protocol):
    """Persistence boundary required by :class:`MarketDataIngestionService`."""

    async def existing_trading_dates(self, source: str, symbol: str) -> set[date]:
        """Return the set of trading dates already stored for ``(source, symbol)``."""
        ...

    async def save_many(self, source: str, bars: list[DailyBar]) -> int:
        """Persist ``bars`` for ``source``, skipping any already stored. Returns rows inserted."""
        ...


def _empty_rejections() -> dict[RejectionReason, int]:
    return {}


@dataclass(frozen=True, slots=True)
class SymbolIngestionResult:
    """Per-symbol outcome of one ingestion run."""

    symbol: str
    stored_count: int
    skipped_existing_count: int
    rejected_count: int
    rejections: dict[RejectionReason, int] = field(default_factory=_empty_rejections)
    error: str | None = None


@dataclass(frozen=True, slots=True)
class IngestionRunResult:
    """Outcome of one ingestion run across the whole watchlist."""

    results: list[SymbolIngestionResult]


class MarketDataIngestionService:
    """Fetches, validates, and persists daily bars for a configured watchlist.

    A single symbol's provider failure is isolated (recorded on that symbol's result) and does
    not abort the run for the remaining symbols.
    """

    def __init__(
        self,
        provider: DailyBarProvider,
        repository: DailyBarRepository,
        *,
        source: str,
        calendar_name: str,
        max_latest_bar_staleness_trading_days: int,
        as_of: date | None = None,
    ) -> None:
        self._provider = provider
        self._repository = repository
        self._source = source
        self._calendar_name = calendar_name
        self._max_staleness = max_latest_bar_staleness_trading_days
        self._as_of = as_of

    async def run(self, symbols: list[str]) -> IngestionRunResult:
        """Ingest daily bars for every symbol in ``symbols``, in order."""

        results = [await self._ingest_symbol(symbol) for symbol in symbols]
        return IngestionRunResult(results=results)

    async def _ingest_symbol(self, symbol: str) -> SymbolIngestionResult:
        try:
            bars = await self._provider.fetch_daily_bars(symbol)
        except ProviderError as exc:
            logger.warning(
                "market_data_ingestion_provider_error",
                extra={"symbol": symbol, "error": str(exc)},
            )
            return SymbolIngestionResult(
                symbol=symbol,
                stored_count=0,
                skipped_existing_count=0,
                rejected_count=0,
                error=str(exc),
            )

        if not bars:
            return SymbolIngestionResult(
                symbol=symbol, stored_count=0, skipped_existing_count=0, rejected_count=0
            )

        as_of = self._as_of if self._as_of is not None else date.today()
        latest_trading_date = max(bar.trading_date for bar in bars)
        existing_dates = await self._repository.existing_trading_dates(self._source, symbol)

        valid_bars: list[DailyBar] = []
        rejections: dict[RejectionReason, int] = {}
        skipped_existing = 0

        for bar in bars:
            if bar.trading_date in existing_dates:
                skipped_existing += 1
                continue

            result = validate_daily_bar(
                bar,
                calendar_name=self._calendar_name,
                as_of=as_of,
                max_staleness_trading_days=self._max_staleness,
                is_latest_bar=bar.trading_date == latest_trading_date,
            )
            if result.is_valid:
                valid_bars.append(bar)
                continue

            reason = result.reason
            if reason is not None:
                rejections[reason] = rejections.get(reason, 0) + 1
            logger.info(
                "market_data_bar_rejected",
                extra={
                    "symbol": symbol,
                    "trading_date": bar.trading_date.isoformat(),
                    "reason": reason.value if reason is not None else None,
                    "detail": result.detail,
                },
            )

        stored_count = 0
        if valid_bars:
            stored_count = await self._repository.save_many(self._source, valid_bars)

        return SymbolIngestionResult(
            symbol=symbol,
            stored_count=stored_count,
            skipped_existing_count=skipped_existing,
            rejected_count=sum(rejections.values()),
            rejections=rejections,
        )
