"""Market data ingestion orchestration.

Depends only on :class:`~aegis.providers.market_data.DailyBarProvider` and the
:class:`DailyBarRepository` protocol defined below, per the domain/persistence module boundary
in ``docs/architecture/overview.md``: no FastAPI or SQLAlchemy import belongs in this module.
The concrete repository (``aegis.persistence.repositories.market_data``) satisfies this
protocol structurally without either module importing the other.

Optional secondary-provider tip catch-up (ADR-0011 / ADR-0262) stays in this service so each
successful write uses the producing adapter's ``source`` without silent provenance swaps.
When a secondary is configured, both providers are refreshed independently per symbol so a
primary rate-limit or lagging primary tip cannot hide a fresher secondary tip.

Provider historical corrections (ADR-0013) insert append-only ``correction`` rows when a
re-ingest materially differs from the current stored bar for the same trading date.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Protocol

from aegis.domain.market_data_corrections import StoredBarSnapshot, bars_materially_differ
from aegis.domain.market_data_validation import RejectionReason, validate_daily_bar
from aegis.providers.errors import ProviderError
from aegis.providers.market_data import DailyBar, DailyBarProvider

logger = logging.getLogger(__name__)


class DailyBarRepository(Protocol):
    """Persistence boundary required by :class:`MarketDataIngestionService`."""

    async def get_current_by_trading_dates(
        self,
        source: str,
        symbol: str,
        trading_dates: set[date],
    ) -> dict[date, StoredBarSnapshot]:
        """Return current stored observations keyed by trading date."""
        ...

    async def save_many(self, source: str, bars: list[DailyBar]) -> int:
        """Persist ``initial`` observations. Returns rows inserted."""
        ...

    async def save_corrections(
        self,
        source: str,
        corrections: list[tuple[DailyBar, int]],
    ) -> int:
        """Persist ``correction`` rows superseding prior observations. Returns rows inserted."""
        ...


def _empty_rejections() -> dict[RejectionReason, int]:
    return {}


@dataclass(frozen=True, slots=True)
class SymbolIngestionResult:
    """Per-symbol outcome of one ingestion run."""

    symbol: str
    stored_count: int
    skipped_existing_count: int
    corrected_count: int
    rejected_count: int
    rejections: dict[RejectionReason, int] = field(default_factory=_empty_rejections)
    error: str | None = None
    latest_trading_date: date | None = None
    latest_trading_date_source: str | None = None


@dataclass(frozen=True, slots=True)
class IngestionRunResult:
    """Outcome of one ingestion run across the whole watchlist."""

    results: list[SymbolIngestionResult]


class MarketDataIngestionService:
    """Fetches, validates, and persists daily bars for a configured watchlist.

    A single symbol's provider failure is isolated (recorded on that symbol's result) and does
    not abort the run for the remaining symbols. When a secondary provider is configured,
    both primary and secondary are refreshed independently per symbol; successful writes
    always use that adapter's ``source`` (ADR-0011 / ADR-0262).

    Re-ingest of an identical stored bar is a silent skip; material provider revisions insert
  a new ``correction`` row (ADR-0013).
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
        secondary_provider: DailyBarProvider | None = None,
        secondary_source: str | None = None,
        correction_price_epsilon: Decimal = Decimal("1e-6"),
    ) -> None:
        self._provider = provider
        self._repository = repository
        self._source = source
        self._calendar_name = calendar_name
        self._max_staleness = max_latest_bar_staleness_trading_days
        self._as_of = as_of
        self._secondary_provider = secondary_provider
        self._secondary_source = secondary_source
        self._correction_price_epsilon = correction_price_epsilon

    async def run(self, symbols: list[str]) -> IngestionRunResult:
        """Ingest daily bars for every symbol in ``symbols``, in order."""

        results = [await self._ingest_symbol(symbol) for symbol in symbols]
        return IngestionRunResult(results=results)

    async def _ingest_symbol(self, symbol: str) -> SymbolIngestionResult:
        primary = await self._ingest_from_provider(symbol, self._provider, self._source)
        if self._secondary_provider is None or self._secondary_source is None:
            return primary

        secondary = await self._ingest_from_provider(
            symbol,
            self._secondary_provider,
            self._secondary_source,
        )
        return _merge_symbol_results(symbol, primary, secondary)

    async def _ingest_from_provider(
        self,
        symbol: str,
        provider: DailyBarProvider,
        source: str,
    ) -> SymbolIngestionResult:
        try:
            bars = await provider.fetch_daily_bars(symbol)
        except ProviderError as exc:
            logger.warning(
                "market_data_ingestion_provider_error",
                extra={
                    "symbol": symbol,
                    "source": source,
                    "error": str(exc),
                },
            )
            return SymbolIngestionResult(
                symbol=symbol,
                stored_count=0,
                skipped_existing_count=0,
                corrected_count=0,
                rejected_count=0,
                error=str(exc),
            )

        if not bars:
            return SymbolIngestionResult(
                symbol=symbol,
                stored_count=0,
                skipped_existing_count=0,
                corrected_count=0,
                rejected_count=0,
            )

        as_of = self._as_of if self._as_of is not None else date.today()
        latest_trading_date = max(bar.trading_date for bar in bars)
        trading_dates = {bar.trading_date for bar in bars}
        current_by_date = await self._repository.get_current_by_trading_dates(
            source, symbol, trading_dates
        )

        valid_initial: list[DailyBar] = []
        valid_corrections: list[tuple[DailyBar, int]] = []
        rejections: dict[RejectionReason, int] = {}
        skipped_existing = 0

        for bar in bars:
            current = current_by_date.get(bar.trading_date)
            if current is None:
                outcome = _validate_bar(
                    bar,
                    calendar_name=self._calendar_name,
                    as_of=as_of,
                    max_staleness=self._max_staleness,
                    is_latest_bar=bar.trading_date == latest_trading_date,
                )
                if outcome.is_valid:
                    valid_initial.append(bar)
                else:
                    _record_rejection(
                        rejections,
                        outcome.reason,
                        symbol=symbol,
                        trading_date=bar.trading_date,
                        source=source,
                        detail=outcome.detail,
                    )
                continue

            if not bars_materially_differ(
                current,
                bar,
                price_epsilon=self._correction_price_epsilon,
            ):
                skipped_existing += 1
                continue

            outcome = _validate_bar(
                bar,
                calendar_name=self._calendar_name,
                as_of=as_of,
                max_staleness=self._max_staleness,
                is_latest_bar=bar.trading_date == latest_trading_date,
            )
            if outcome.is_valid:
                valid_corrections.append((bar, current.id))
                logger.info(
                    "market_data_correction_applied",
                    extra={
                        "symbol": symbol,
                        "trading_date": bar.trading_date.isoformat(),
                        "source": source,
                        "supersedes_observation_id": current.id,
                    },
                )
            else:
                _record_rejection(
                    rejections,
                    outcome.reason,
                    symbol=symbol,
                    trading_date=bar.trading_date,
                    source=source,
                    detail=outcome.detail,
                )

        stored_count = 0
        if valid_initial:
            stored_count = await self._repository.save_many(source, valid_initial)

        corrected_count = 0
        if valid_corrections:
            corrected_count = await self._repository.save_corrections(source, valid_corrections)

        return SymbolIngestionResult(
            symbol=symbol,
            stored_count=stored_count,
            skipped_existing_count=skipped_existing,
            corrected_count=corrected_count,
            rejected_count=sum(rejections.values()),
            rejections=rejections,
            latest_trading_date=latest_trading_date,
            latest_trading_date_source=source,
        )


def _merge_symbol_results(
    symbol: str,
    primary: SymbolIngestionResult,
    secondary: SymbolIngestionResult,
) -> SymbolIngestionResult:
    """Combine independent primary/secondary outcomes for one symbol (ADR-0262)."""

    primary_ok = primary.error is None
    secondary_ok = secondary.error is None
    if not primary_ok and not secondary_ok:
        return SymbolIngestionResult(
            symbol=symbol,
            stored_count=0,
            skipped_existing_count=0,
            corrected_count=0,
            rejected_count=0,
            error=(
                f"primary ({primary.error}); secondary ({secondary.error})"
                if primary.error and secondary.error
                else (primary.error or secondary.error)
            ),
        )

    parts = [part for part in (primary, secondary) if part.error is None]
    rejections: dict[RejectionReason, int] = {}
    for part in parts:
        for reason, count in part.rejections.items():
            rejections[reason] = rejections.get(reason, 0) + count

    latest_trading_date: date | None = None
    latest_trading_date_source: str | None = None
    for part in parts:
        tip = part.latest_trading_date
        if tip is None:
            continue
        if latest_trading_date is None or tip > latest_trading_date:
            latest_trading_date = tip
            latest_trading_date_source = part.latest_trading_date_source
        elif tip == latest_trading_date and latest_trading_date_source is None:
            latest_trading_date_source = part.latest_trading_date_source

    if not primary_ok:
        logger.warning(
            "market_data_ingestion_primary_failed_secondary_used",
            extra={
                "symbol": symbol,
                "primary_error": primary.error,
                "latest_trading_date": (
                    latest_trading_date.isoformat() if latest_trading_date else None
                ),
                "latest_trading_date_source": latest_trading_date_source,
            },
        )
    elif not secondary_ok:
        logger.warning(
            "market_data_ingestion_secondary_failed_primary_used",
            extra={
                "symbol": symbol,
                "secondary_error": secondary.error,
                "latest_trading_date": (
                    latest_trading_date.isoformat() if latest_trading_date else None
                ),
                "latest_trading_date_source": latest_trading_date_source,
            },
        )

    return SymbolIngestionResult(
        symbol=symbol,
        stored_count=sum(part.stored_count for part in parts),
        skipped_existing_count=sum(part.skipped_existing_count for part in parts),
        corrected_count=sum(part.corrected_count for part in parts),
        rejected_count=sum(part.rejected_count for part in parts),
        rejections=rejections,
        latest_trading_date=latest_trading_date,
        latest_trading_date_source=latest_trading_date_source,
    )


@dataclass(frozen=True, slots=True)
class _ValidationOutcome:
    is_valid: bool
    reason: RejectionReason | None = None
    detail: str | None = None


def _validate_bar(
    bar: DailyBar,
    *,
    calendar_name: str,
    as_of: date,
    max_staleness: int,
    is_latest_bar: bool,
) -> _ValidationOutcome:
    result = validate_daily_bar(
        bar,
        calendar_name=calendar_name,
        as_of=as_of,
        max_staleness_trading_days=max_staleness,
        is_latest_bar=is_latest_bar,
    )
    return _ValidationOutcome(
        is_valid=result.is_valid,
        reason=result.reason,
        detail=result.detail,
    )


def _record_rejection(
    rejections: dict[RejectionReason, int],
    reason: RejectionReason | None,
    *,
    symbol: str,
    trading_date: date,
    source: str,
    detail: str | None,
) -> None:
    if reason is not None:
        rejections[reason] = rejections.get(reason, 0) + 1
    logger.info(
        "market_data_bar_rejected",
        extra={
            "symbol": symbol,
            "trading_date": trading_date.isoformat(),
            "reason": reason.value if reason is not None else None,
            "detail": detail,
            "source": source,
        },
    )
