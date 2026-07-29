"""Research probability calibration (Phase 15, ADR-0016).

Framework-free empirical calibration from stored labeled assessment history. Sets a bounded
``probability_confidence`` on append-only calibration rows; does not merge with coverage
confidence or promote assessments beyond ``research_only``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol

from aegis.domain.research_assessment import (
    METHOD_ID,
    STATE_RESEARCH_ONLY,
    ResearchAssessmentSnapshotData,
)
from aegis.domain.research_outcome_labels import LABEL_METHOD_ID

logger = logging.getLogger(__name__)

CALIBRATION_METHOD_ID = "research_calibration_v1"
CALIBRATION_METHOD_VERSION = 1
CALIBRATION_SCHEMA_VERSION = 1
STATE_RESEARCH_ONLY_CALIBRATION = STATE_RESEARCH_ONLY
OUTCOME_HORIZON_KEY = "forward_return_5"
RESEARCH_INDEX_KEY = "research_index"


class CalibrationReason(StrEnum):
    """Structured fail-closed reason codes."""

    ASSESSMENT_NOT_FOUND = "assessment_not_found"
    MISSING_RESEARCH_INDEX = "missing_research_index"
    INSUFFICIENT_LABELED_CORPUS = "insufficient_labeled_corpus"
    INSUFFICIENT_SIMILAR_EXAMPLES = "insufficient_similar_examples"


class CalibrationUnavailableError(Exception):
    """Raised when calibration cannot be computed; callers must persist nothing."""

    def __init__(self, reason: CalibrationReason, detail: str) -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(detail)


@dataclass(frozen=True, slots=True)
class LabeledResearchExample:
    """One historical assessment paired with its forward-return label."""

    assessment_snapshot_id: int
    research_index: float
    forward_return_5: float


@dataclass(frozen=True, slots=True)
class ProbabilityCalibrationData:
    """A successful calibration row ready for append-only persistence."""

    assessment_snapshot_id: int
    symbol: str
    calibration_method_id: str
    calibration_method_version: int
    state: str
    computed_at: datetime
    probability_confidence: float
    corpus_count: int
    bucket_count: int
    schema_version: int
    id: int | None = None


def compute_research_calibration_v1(
    snapshot: ResearchAssessmentSnapshotData,
    corpus: list[LabeledResearchExample],
    *,
    min_corpus: int,
    min_bucket: int,
    index_bucket_width: float,
) -> ProbabilityCalibrationData:
    """Compute empirical positive-rate calibration or raise fail-closed."""

    if snapshot.id is None:
        raise CalibrationUnavailableError(
            CalibrationReason.ASSESSMENT_NOT_FOUND,
            "assessment snapshot id is required to attach calibration",
        )

    research_index = _research_index_from_snapshot(snapshot)
    historical = [
        example
        for example in corpus
        if example.assessment_snapshot_id != snapshot.id
    ]

    if len(historical) < min_corpus:
        raise CalibrationUnavailableError(
            CalibrationReason.INSUFFICIENT_LABELED_CORPUS,
            f"need at least {min_corpus} labeled historical examples, found {len(historical)}",
        )

    bucket = [
        example
        for example in historical
        if abs(example.research_index - research_index) <= index_bucket_width
    ]
    if len(bucket) < min_bucket:
        raise CalibrationUnavailableError(
            CalibrationReason.INSUFFICIENT_SIMILAR_EXAMPLES,
            (
                f"need at least {min_bucket} examples within research_index "
                f"±{index_bucket_width}, found {len(bucket)}"
            ),
        )

    positive_count = sum(1 for example in bucket if example.forward_return_5 > 0)
    probability = _clip01(positive_count / len(bucket))

    return ProbabilityCalibrationData(
        assessment_snapshot_id=snapshot.id,
        symbol=snapshot.symbol,
        calibration_method_id=CALIBRATION_METHOD_ID,
        calibration_method_version=CALIBRATION_METHOD_VERSION,
        state=STATE_RESEARCH_ONLY_CALIBRATION,
        computed_at=datetime.now(tz=UTC),
        probability_confidence=probability,
        corpus_count=len(historical),
        bucket_count=len(bucket),
        schema_version=CALIBRATION_SCHEMA_VERSION,
    )


def _research_index_from_snapshot(snapshot: ResearchAssessmentSnapshotData) -> float:
    value = snapshot.components.get(RESEARCH_INDEX_KEY)
    if not isinstance(value, (int, float)):
        raise CalibrationUnavailableError(
            CalibrationReason.MISSING_RESEARCH_INDEX,
            f"component {RESEARCH_INDEX_KEY!r} is required for calibration",
        )
    return float(value)


def _clip01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class LabeledCorpusReader(Protocol):
    async def list_labeled_examples(
        self, symbol: str, limit: int
    ) -> list[LabeledResearchExample]:
        ...


class AssessmentReaderForCalibration(Protocol):
    async def get_by_id(self, assessment_snapshot_id: int) -> ResearchAssessmentSnapshotData | None:
        ...


class ProbabilityCalibrationStore(Protocol):
    async def insert(self, calibration: ProbabilityCalibrationData) -> ProbabilityCalibrationData:
        ...

    async def get_latest_for_assessment(
        self, assessment_snapshot_id: int
    ) -> ProbabilityCalibrationData | None:
        ...


class ResearchProbabilityCalibrationService:
    """Load assessment + labeled corpus, compute calibration, append on success."""

    def __init__(
        self,
        assessment_store: AssessmentReaderForCalibration,
        corpus_reader: LabeledCorpusReader,
        calibration_store: ProbabilityCalibrationStore,
        *,
        min_corpus: int,
        min_bucket: int,
        index_bucket_width: float,
        corpus_limit: int = 500,
    ) -> None:
        self._assessment_store = assessment_store
        self._corpus_reader = corpus_reader
        self._calibration_store = calibration_store
        self._min_corpus = min_corpus
        self._min_bucket = min_bucket
        self._index_bucket_width = index_bucket_width
        self._corpus_limit = corpus_limit

    async def calibrate_assessment(
        self, symbol: str, assessment_snapshot_id: int
    ) -> ProbabilityCalibrationData:
        snapshot = await self._assessment_store.get_by_id(assessment_snapshot_id)
        if snapshot is None or snapshot.symbol.upper() != symbol.upper():
            raise CalibrationUnavailableError(
                CalibrationReason.ASSESSMENT_NOT_FOUND,
                f"no assessment {assessment_snapshot_id} for symbol {symbol!r}",
            )
        if snapshot.method_id != METHOD_ID:
            raise CalibrationUnavailableError(
                CalibrationReason.ASSESSMENT_NOT_FOUND,
                f"assessment method {snapshot.method_id!r} is not supported for calibration",
            )

        corpus = await self._corpus_reader.list_labeled_examples(
            symbol.upper(),
            self._corpus_limit,
        )
        calibration = compute_research_calibration_v1(
            snapshot,
            corpus,
            min_corpus=self._min_corpus,
            min_bucket=self._min_bucket,
            index_bucket_width=self._index_bucket_width,
        )
        logger.info(
            "research_probability_calibration_computed",
            extra={
                "symbol": symbol.upper(),
                "assessment_snapshot_id": assessment_snapshot_id,
                "probability_confidence": calibration.probability_confidence,
                "corpus_count": calibration.corpus_count,
                "bucket_count": calibration.bucket_count,
            },
        )
        return await self._calibration_store.insert(calibration)

    async def latest_calibration_for_assessment(
        self, assessment_snapshot_id: int
    ) -> ProbabilityCalibrationData | None:
        return await self._calibration_store.get_latest_for_assessment(assessment_snapshot_id)


def apply_probability_calibration(
    snapshot: ResearchAssessmentSnapshotData,
    calibration: ProbabilityCalibrationData | None,
) -> ResearchAssessmentSnapshotData:
    """Overlay the latest calibration onto a snapshot for API presentation."""

    if calibration is None:
        return snapshot
    return ResearchAssessmentSnapshotData(
        id=snapshot.id,
        symbol=snapshot.symbol,
        method_id=snapshot.method_id,
        method_version=snapshot.method_version,
        state=snapshot.state,
        as_of_trading_date=snapshot.as_of_trading_date,
        event_time=snapshot.event_time,
        computed_at=snapshot.computed_at,
        coverage_confidence=snapshot.coverage_confidence,
        probability_confidence=calibration.probability_confidence,
        components=snapshot.components,
        schema_version=snapshot.schema_version,
        input_source=snapshot.input_source,
        lookback_start_date=snapshot.lookback_start_date,
        lookback_end_date=snapshot.lookback_end_date,
        bar_count=snapshot.bar_count,
    )


# Label method filter constants for corpus queries (Phase 13).
EXPECTED_LABEL_METHOD_ID = LABEL_METHOD_ID
