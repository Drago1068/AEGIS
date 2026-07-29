"""Repository for append-only research assessment snapshots (Phase 6, ADR-0007)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aegis.domain.research_assessment import ResearchAssessmentSnapshotData
from aegis.persistence.models import ResearchAssessmentSnapshot


class ResearchAssessmentRepository:
    """SQLAlchemy-backed insert-only storage for research assessment snapshots."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def insert(
        self, snapshot: ResearchAssessmentSnapshotData
    ) -> ResearchAssessmentSnapshotData:
        """Append ``snapshot``; never update an existing row."""

        row = ResearchAssessmentSnapshot(
            computed_at=snapshot.computed_at,
            as_of_trading_date=snapshot.as_of_trading_date,
            event_time=snapshot.event_time,
            symbol=snapshot.symbol,
            method_id=snapshot.method_id,
            method_version=snapshot.method_version,
            state=snapshot.state,
            coverage_confidence=snapshot.coverage_confidence,
            probability_confidence=snapshot.probability_confidence,
            components=dict(snapshot.components),
            schema_version=snapshot.schema_version,
            input_source=snapshot.input_source,
            lookback_start_date=snapshot.lookback_start_date,
            lookback_end_date=snapshot.lookback_end_date,
            bar_count=snapshot.bar_count,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_data(row)

    async def list_recent(
        self, symbol: str, limit: int
    ) -> list[ResearchAssessmentSnapshotData]:
        """Return up to ``limit`` snapshots for ``symbol``, newest ``computed_at`` first."""

        stmt = (
            select(ResearchAssessmentSnapshot)
            .where(ResearchAssessmentSnapshot.symbol == symbol)
            .order_by(ResearchAssessmentSnapshot.computed_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_to_data(row) for row in result.scalars().all()]

    async def get_latest(self, symbol: str) -> ResearchAssessmentSnapshotData | None:
        """Return the newest snapshot for ``symbol``, or ``None``."""

        rows = await self.list_recent(symbol, 1)
        return rows[0] if rows else None


def _to_data(row: ResearchAssessmentSnapshot) -> ResearchAssessmentSnapshotData:
    components_raw = row.components
    components: dict[str, float] = {}
    for key, value in components_raw.items():
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise TypeError(f"component {key!r} must be numeric, got {type(value)!r}")
        components[str(key)] = float(value)
    return ResearchAssessmentSnapshotData(
        symbol=row.symbol,
        method_id=row.method_id,
        method_version=row.method_version,
        state=row.state,
        as_of_trading_date=row.as_of_trading_date,
        event_time=row.event_time,
        computed_at=row.computed_at,
        coverage_confidence=float(row.coverage_confidence),
        probability_confidence=(
            None
            if row.probability_confidence is None
            else float(row.probability_confidence)
        ),
        components=components,
        schema_version=row.schema_version,
        input_source=row.input_source,
        lookback_start_date=row.lookback_start_date,
        lookback_end_date=row.lookback_end_date,
        bar_count=row.bar_count,
    )
