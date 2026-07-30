"""Repository for append-only research assessment outcome labels (Phase 13, ADR-0014)."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aegis.domain.research_outcome_labels import OutcomeLabelData
from aegis.persistence.models import ResearchAssessmentOutcomeLabel


class ResearchOutcomeLabelRepository:
    """SQLAlchemy-backed insert-only storage for outcome labels."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def insert(self, label: OutcomeLabelData) -> OutcomeLabelData:
        row = ResearchAssessmentOutcomeLabel(
            assessment_snapshot_id=label.assessment_snapshot_id,
            computed_at=label.computed_at,
            symbol=label.symbol,
            label_method_id=label.label_method_id,
            label_method_version=label.label_method_version,
            state=label.state,
            as_of_trading_date=label.as_of_trading_date,
            labels=dict(label.labels),
            label_end_dates=dict(label.label_end_dates),
            schema_version=label.schema_version,
            bar_source=label.bar_source,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_data(row)

    async def get_latest_for_assessment(
        self, assessment_snapshot_id: int
    ) -> OutcomeLabelData | None:
        rows = await self.list_for_assessment(assessment_snapshot_id, limit=1)
        return rows[0] if rows else None

    async def list_for_assessment(
        self,
        assessment_snapshot_id: int,
        limit: int,
        *,
        symbol: str | None = None,
    ) -> list[OutcomeLabelData]:
        """Return up to ``limit`` labels for an assessment, newest first.

        When ``symbol`` is set, only rows for that symbol (case-insensitive) are returned.
        """

        conditions = [
            ResearchAssessmentOutcomeLabel.assessment_snapshot_id == assessment_snapshot_id
        ]
        if symbol is not None:
            conditions.append(ResearchAssessmentOutcomeLabel.symbol == symbol.upper())
        stmt = (
            select(ResearchAssessmentOutcomeLabel)
            .where(*conditions)
            .order_by(ResearchAssessmentOutcomeLabel.computed_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_to_data(row) for row in result.scalars().all()]

    async def assessment_ids_with_labels(
        self,
        symbol: str,
        assessment_ids: Sequence[int],
        *,
        label_method_id: str,
    ) -> set[int]:
        """Return the subset of ``assessment_ids`` that already have a matching label row."""

        if not assessment_ids:
            return set()
        stmt = (
            select(ResearchAssessmentOutcomeLabel.assessment_snapshot_id)
            .where(
                ResearchAssessmentOutcomeLabel.symbol == symbol.upper(),
                ResearchAssessmentOutcomeLabel.label_method_id == label_method_id,
                ResearchAssessmentOutcomeLabel.assessment_snapshot_id.in_(
                    list(assessment_ids)
                ),
            )
            .distinct()
        )
        result = await self._session.execute(stmt)
        return {int(row) for row in result.scalars().all()}


def _to_data(row: ResearchAssessmentOutcomeLabel) -> OutcomeLabelData:
    labels: dict[str, float] = {}
    for key, value in row.labels.items():
        if isinstance(value, (int, float)):
            labels[str(key)] = float(value)
        else:
            labels[str(key)] = float(str(value))
    label_end_dates = {str(k): str(v) for k, v in row.label_end_dates.items()}
    return OutcomeLabelData(
        id=row.id,
        assessment_snapshot_id=row.assessment_snapshot_id,
        symbol=row.symbol,
        label_method_id=row.label_method_id,
        label_method_version=row.label_method_version,
        state=row.state,
        as_of_trading_date=row.as_of_trading_date,
        computed_at=row.computed_at,
        labels=labels,
        label_end_dates=label_end_dates,
        schema_version=row.schema_version,
        bar_source=row.bar_source,
    )
