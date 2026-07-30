"""Repository for labeled research corpus and probability calibrations (Phase 15)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aegis.domain.research_outcome_labels import LABEL_METHOD_VERSION
from aegis.domain.research_probability_calibration import (
    EXPECTED_LABEL_METHOD_ID,
    OUTCOME_HORIZON_KEY,
    RESEARCH_INDEX_KEY,
    LabeledResearchExample,
    ProbabilityCalibrationData,
)
from aegis.persistence.models import (
    ResearchAssessmentOutcomeLabel,
    ResearchAssessmentProbabilityCalibration,
    ResearchAssessmentSnapshot,
)


class ResearchProbabilityCalibrationRepository:
    """SQLAlchemy-backed labeled corpus reads and append-only calibration storage."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_labeled_examples(self, symbol: str, limit: int) -> list[LabeledResearchExample]:
        """Return labeled examples with newest label per assessment."""

        stmt = (
            select(ResearchAssessmentOutcomeLabel, ResearchAssessmentSnapshot)
            .join(
                ResearchAssessmentSnapshot,
                ResearchAssessmentSnapshot.id
                == ResearchAssessmentOutcomeLabel.assessment_snapshot_id,
            )
            .where(
                ResearchAssessmentOutcomeLabel.symbol == symbol.upper(),
                ResearchAssessmentOutcomeLabel.label_method_id == EXPECTED_LABEL_METHOD_ID,
                ResearchAssessmentOutcomeLabel.label_method_version == LABEL_METHOD_VERSION,
            )
            .order_by(ResearchAssessmentOutcomeLabel.computed_at.desc())
            .limit(max(limit * 3, limit))
        )
        result = await self._session.execute(stmt)
        examples: list[LabeledResearchExample] = []
        seen_ids: set[int] = set()
        for label_row, assessment_row in result.all():
            assessment_id = label_row.assessment_snapshot_id
            if assessment_id in seen_ids:
                continue
            seen_ids.add(assessment_id)
            research_index = assessment_row.components.get(RESEARCH_INDEX_KEY)
            forward_return = label_row.labels.get(OUTCOME_HORIZON_KEY)
            if not isinstance(research_index, (int, float)):
                continue
            if not isinstance(forward_return, (int, float)):
                continue
            examples.append(
                LabeledResearchExample(
                    assessment_snapshot_id=assessment_id,
                    research_index=float(research_index),
                    forward_return_5=float(forward_return),
                )
            )
            if len(examples) >= limit:
                break
        return examples

    async def insert(self, calibration: ProbabilityCalibrationData) -> ProbabilityCalibrationData:
        row = ResearchAssessmentProbabilityCalibration(
            assessment_snapshot_id=calibration.assessment_snapshot_id,
            computed_at=calibration.computed_at,
            symbol=calibration.symbol,
            calibration_method_id=calibration.calibration_method_id,
            calibration_method_version=calibration.calibration_method_version,
            state=calibration.state,
            probability_confidence=calibration.probability_confidence,
            corpus_count=calibration.corpus_count,
            bucket_count=calibration.bucket_count,
            schema_version=calibration.schema_version,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _calibration_to_data(row)

    async def get_latest_for_assessment(
        self, assessment_snapshot_id: int
    ) -> ProbabilityCalibrationData | None:
        rows = await self.list_for_assessment(assessment_snapshot_id, limit=1)
        return rows[0] if rows else None

    async def list_for_assessment(
        self,
        assessment_snapshot_id: int,
        limit: int,
        *,
        symbol: str | None = None,
    ) -> list[ProbabilityCalibrationData]:
        """Return up to ``limit`` calibrations for an assessment, newest first.

        When ``symbol`` is set, only rows for that symbol (case-insensitive) are returned.
        """

        conditions = [
            ResearchAssessmentProbabilityCalibration.assessment_snapshot_id
            == assessment_snapshot_id
        ]
        if symbol is not None:
            conditions.append(ResearchAssessmentProbabilityCalibration.symbol == symbol.upper())
        stmt = (
            select(ResearchAssessmentProbabilityCalibration)
            .where(*conditions)
            .order_by(ResearchAssessmentProbabilityCalibration.computed_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_calibration_to_data(row) for row in result.scalars().all()]


def _calibration_to_data(
    row: ResearchAssessmentProbabilityCalibration,
) -> ProbabilityCalibrationData:
    return ProbabilityCalibrationData(
        id=row.id,
        assessment_snapshot_id=row.assessment_snapshot_id,
        symbol=row.symbol,
        calibration_method_id=row.calibration_method_id,
        calibration_method_version=row.calibration_method_version,
        state=row.state,
        computed_at=row.computed_at,
        probability_confidence=float(row.probability_confidence),
        corpus_count=row.corpus_count,
        bucket_count=row.bucket_count,
        schema_version=row.schema_version,
    )
