"""Repository for the operational watchlist (which symbols ingestion runs process).

Distinct from ``market_data.py``'s append-only observation store: ``watchlist_symbols`` is a
mutable, soft-deletable operational table, not a point-in-time observation record. See
``docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md``.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from aegis.persistence.models import WatchlistSymbol

_UNIQUE_SYMBOL_CONSTRAINT_NAME = "uq_watchlist_symbols_symbol"


class WatchlistRepository:
    """SQLAlchemy-backed storage for the operational watchlist (see ``persistence.models``).

    ``add``/``ensure_seeded`` use raw Core ``INSERT ... ON CONFLICT`` statements (needed for
    the upsert), which bypass SQLAlchemy's ORM identity map entirely. Because the session
    factory sets ``expire_on_commit=False`` (see ``persistence.database``), an already-loaded
    ORM object for a row a Core statement just changed would otherwise keep serving stale
    in-memory data on the next read within the same session. Every full-entity read below uses
    ``execution_options(populate_existing=True)`` to force a refresh from the query results
    instead of trusting a possibly-stale cached instance.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_active(self) -> list[str]:
        """Return every active symbol, alphabetically. Used by ingestion (on-demand + scheduled)."""

        stmt = (
            select(WatchlistSymbol.symbol)
            .where(WatchlistSymbol.is_active.is_(True))
            .order_by(WatchlistSymbol.symbol)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_active_rows(self) -> list[WatchlistSymbol]:
        """Return every active watchlist row (with metadata), alphabetically by symbol."""

        stmt = (
            select(WatchlistSymbol)
            .where(WatchlistSymbol.is_active.is_(True))
            .order_by(WatchlistSymbol.symbol)
            .execution_options(populate_existing=True)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, symbol: str) -> WatchlistSymbol:
        """Insert ``symbol``, or reactivate it if a (possibly inactive) row already exists."""

        stmt = (
            pg_insert(WatchlistSymbol)
            .values(symbol=symbol, is_active=True)
            .on_conflict_do_update(
                constraint=_UNIQUE_SYMBOL_CONSTRAINT_NAME,
                set_={"is_active": True, "updated_at": func.now()},
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()

        result = await self._session.execute(
            select(WatchlistSymbol)
            .where(WatchlistSymbol.symbol == symbol)
            .execution_options(populate_existing=True)
        )
        return result.scalar_one()

    async def deactivate(self, symbol: str) -> bool:
        """Soft-deactivate ``symbol``. Returns ``True`` if an active row was found and flipped."""

        result = await self._session.execute(
            select(WatchlistSymbol)
            .where(WatchlistSymbol.symbol == symbol, WatchlistSymbol.is_active.is_(True))
            .execution_options(populate_existing=True)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return False

        row.is_active = False
        await self._session.commit()
        return True

    async def ensure_seeded(self, seed_symbols: list[str]) -> None:
        """Insert ``seed_symbols`` only if the table is currently completely empty.

        Runs, in practice, exactly once: after the first row exists (seeded or user-added),
        this is a permanent no-op, even if a user later deactivates every symbol - an empty
        *active* set is a deliberate choice, not something to silently re-seed. See ADR-0003.
        """

        if not seed_symbols:
            return

        total = (
            await self._session.execute(select(func.count()).select_from(WatchlistSymbol))
        ).scalar_one()
        if total > 0:
            return

        values = [{"symbol": symbol, "is_active": True} for symbol in seed_symbols]
        await self._session.execute(pg_insert(WatchlistSymbol).values(values))
        await self._session.commit()
