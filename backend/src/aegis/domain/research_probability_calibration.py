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
CALIBRATION_METHOD_VERSION = 2
CALIBRATION_SCHEMA_VERSION = 1
STATE_RESEARCH_ONLY_CALIBRATION = STATE_RESEARCH_ONLY
OUTCOME_HORIZON_KEYS: tuple[str, ...] = ("forward_return_5", "forward_return_20")
DEFAULT_OUTCOME_HORIZON_KEY = "forward_return_5"
OUTCOME_HORIZON_KEY = DEFAULT_OUTCOME_HORIZON_KEY  # backward-compatible alias
RESEARCH_INDEX_KEY = "research_index"


def normalize_outcome_horizon_key(horizon_key: str | None) -> str:
    """Return a supported horizon key or raise ValueError."""

    key = (horizon_key or DEFAULT_OUTCOME_HORIZON_KEY).strip()
    if key not in OUTCOME_HORIZON_KEYS:
        raise ValueError(
            f"unsupported outcome horizon {key!r}; expected one of {OUTCOME_HORIZON_KEYS}"
        )
    return key


class CalibrationReadinessStatus(StrEnum):
    """Read-only readiness gate status for operator diagnostics (Phase 16)."""

    READY = "ready"
    NO_ASSESSMENT = "no_assessment"
    MISSING_RESEARCH_INDEX = "missing_research_index"
    INSUFFICIENT_LABELED_CORPUS = "insufficient_labeled_corpus"
    INSUFFICIENT_SIMILAR_EXAMPLES = "insufficient_similar_examples"


@dataclass(frozen=True, slots=True)
class CalibrationHorizonReadinessData:
    """Per-horizon corpus-gate diagnostics; never invents probability_confidence."""

    outcome_horizon_key: str
    status: CalibrationReadinessStatus
    corpus_count: int
    bucket_count: int
    detail: str


@dataclass(frozen=True, slots=True)
class CalibrationReadinessData:
    """Corpus-gate diagnostics for a symbol; never invents probability_confidence."""

    symbol: str
    status: CalibrationReadinessStatus
    assessment_snapshot_id: int | None
    research_index: float | None
    corpus_count: int
    bucket_count: int
    min_corpus: int
    min_bucket: int
    index_bucket_width: float
    calibration_method_id: str
    detail: str
    outcome_horizon_key: str = DEFAULT_OUTCOME_HORIZON_KEY
    by_horizon: tuple[CalibrationHorizonReadinessData, ...] = ()


def evaluate_calibration_readiness(
    symbol: str,
    snapshot: ResearchAssessmentSnapshotData | None,
    corpus: list[LabeledResearchExample],
    *,
    min_corpus: int,
    min_bucket: int,
    index_bucket_width: float,
    outcome_horizon_key: str = DEFAULT_OUTCOME_HORIZON_KEY,
) -> CalibrationReadinessData:
    """Report whether research_calibration_v1 gates would pass; persists nothing."""

    horizon = normalize_outcome_horizon_key(outcome_horizon_key)
    normalized = symbol.upper()
    if snapshot is None:
        return CalibrationReadinessData(
            symbol=normalized,
            status=CalibrationReadinessStatus.NO_ASSESSMENT,
            assessment_snapshot_id=None,
            research_index=None,
            corpus_count=0,
            bucket_count=0,
            min_corpus=min_corpus,
            min_bucket=min_bucket,
            index_bucket_width=index_bucket_width,
            calibration_method_id=CALIBRATION_METHOD_ID,
            detail="no research assessment snapshot available",
            outcome_horizon_key=horizon,
        )

    if snapshot.id is None:
        return CalibrationReadinessData(
            symbol=normalized,
            status=CalibrationReadinessStatus.NO_ASSESSMENT,
            assessment_snapshot_id=None,
            research_index=None,
            corpus_count=0,
            bucket_count=0,
            min_corpus=min_corpus,
            min_bucket=min_bucket,
            index_bucket_width=index_bucket_width,
            calibration_method_id=CALIBRATION_METHOD_ID,
            detail="assessment snapshot id is required for calibration readiness",
            outcome_horizon_key=horizon,
        )

    research_index_raw = snapshot.components.get(RESEARCH_INDEX_KEY)
    if not isinstance(research_index_raw, (int, float)):
        return CalibrationReadinessData(
            symbol=normalized,
            status=CalibrationReadinessStatus.MISSING_RESEARCH_INDEX,
            assessment_snapshot_id=snapshot.id,
            research_index=None,
            corpus_count=0,
            bucket_count=0,
            min_corpus=min_corpus,
            min_bucket=min_bucket,
            index_bucket_width=index_bucket_width,
            calibration_method_id=CALIBRATION_METHOD_ID,
            detail=f"component {RESEARCH_INDEX_KEY!r} is required for calibration",
            outcome_horizon_key=horizon,
        )

    research_index = float(research_index_raw)
    historical = [example for example in corpus if example.assessment_snapshot_id != snapshot.id]
    bucket = [
        example
        for example in historical
        if abs(example.research_index - research_index) <= index_bucket_width
    ]

    if len(historical) < min_corpus:
        return CalibrationReadinessData(
            symbol=normalized,
            status=CalibrationReadinessStatus.INSUFFICIENT_LABELED_CORPUS,
            assessment_snapshot_id=snapshot.id,
            research_index=research_index,
            corpus_count=len(historical),
            bucket_count=len(bucket),
            min_corpus=min_corpus,
            min_bucket=min_bucket,
            index_bucket_width=index_bucket_width,
            calibration_method_id=CALIBRATION_METHOD_ID,
            detail=(
                f"need at least {min_corpus} labeled historical examples for {horizon}, "
                f"found {len(historical)}"
            ),
            outcome_horizon_key=horizon,
        )

    if len(bucket) < min_bucket:
        return CalibrationReadinessData(
            symbol=normalized,
            status=CalibrationReadinessStatus.INSUFFICIENT_SIMILAR_EXAMPLES,
            assessment_snapshot_id=snapshot.id,
            research_index=research_index,
            corpus_count=len(historical),
            bucket_count=len(bucket),
            min_corpus=min_corpus,
            min_bucket=min_bucket,
            index_bucket_width=index_bucket_width,
            calibration_method_id=CALIBRATION_METHOD_ID,
            detail=(
                f"need at least {min_bucket} examples within research_index "
                f"±{index_bucket_width} for {horizon}, found {len(bucket)}"
            ),
            outcome_horizon_key=horizon,
        )

    return CalibrationReadinessData(
        symbol=normalized,
        status=CalibrationReadinessStatus.READY,
        assessment_snapshot_id=snapshot.id,
        research_index=research_index,
        corpus_count=len(historical),
        bucket_count=len(bucket),
        min_corpus=min_corpus,
        min_bucket=min_bucket,
        index_bucket_width=index_bucket_width,
        calibration_method_id=CALIBRATION_METHOD_ID,
        detail=(
            f"corpus and similarity bucket gates would pass for research_calibration_v1 "
            f"({horizon})"
        ),
        outcome_horizon_key=horizon,
    )


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
    """One historical assessment paired with a forward-return label for one horizon."""

    assessment_snapshot_id: int
    research_index: float
    forward_return: float
    outcome_horizon_key: str = DEFAULT_OUTCOME_HORIZON_KEY


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
    outcome_horizon_key: str = DEFAULT_OUTCOME_HORIZON_KEY
    id: int | None = None


def compute_research_calibration_v1(
    snapshot: ResearchAssessmentSnapshotData,
    corpus: list[LabeledResearchExample],
    *,
    min_corpus: int,
    min_bucket: int,
    index_bucket_width: float,
    outcome_horizon_key: str = DEFAULT_OUTCOME_HORIZON_KEY,
) -> ProbabilityCalibrationData:
    """Compute empirical positive-rate calibration or raise fail-closed."""

    horizon = normalize_outcome_horizon_key(outcome_horizon_key)
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
        and example.outcome_horizon_key == horizon
    ]

    if len(historical) < min_corpus:
        raise CalibrationUnavailableError(
            CalibrationReason.INSUFFICIENT_LABELED_CORPUS,
            (
                f"need at least {min_corpus} labeled historical examples for {horizon}, "
                f"found {len(historical)}"
            ),
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
                f"±{index_bucket_width} for {horizon}, found {len(bucket)}"
            ),
        )

    positive_count = sum(1 for example in bucket if example.forward_return > 0)
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
        outcome_horizon_key=horizon,
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
        self,
        symbol: str,
        limit: int,
        *,
        outcome_horizon_key: str = DEFAULT_OUTCOME_HORIZON_KEY,
    ) -> list[LabeledResearchExample]: ...


class AssessmentReaderForCalibration(Protocol):
    async def get_by_id(
        self, assessment_snapshot_id: int
    ) -> ResearchAssessmentSnapshotData | None: ...


class ProbabilityCalibrationStore(Protocol):
    async def insert(
        self, calibration: ProbabilityCalibrationData
    ) -> ProbabilityCalibrationData: ...

    async def get_latest_for_assessment(
        self, assessment_snapshot_id: int
    ) -> ProbabilityCalibrationData | None: ...

    async def list_for_assessment(
        self,
        assessment_snapshot_id: int,
        limit: int,
        *,
        symbol: str | None = None,
    ) -> list[ProbabilityCalibrationData]: ...


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
        self,
        symbol: str,
        assessment_snapshot_id: int,
        *,
        outcome_horizon_key: str = DEFAULT_OUTCOME_HORIZON_KEY,
    ) -> ProbabilityCalibrationData:
        horizon = normalize_outcome_horizon_key(outcome_horizon_key)
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
            outcome_horizon_key=horizon,
        )
        calibration = compute_research_calibration_v1(
            snapshot,
            corpus,
            min_corpus=self._min_corpus,
            min_bucket=self._min_bucket,
            index_bucket_width=self._index_bucket_width,
            outcome_horizon_key=horizon,
        )
        logger.info(
            "research_probability_calibration_computed",
            extra={
                "symbol": symbol.upper(),
                "assessment_snapshot_id": assessment_snapshot_id,
                "outcome_horizon_key": horizon,
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

    async def list_calibrations_for_assessment(
        self,
        symbol: str,
        assessment_snapshot_id: int,
        limit: int,
    ) -> list[ProbabilityCalibrationData]:
        """Return up to ``limit`` calibrations for ``assessment_snapshot_id`` and ``symbol``."""

        return await self._calibration_store.list_for_assessment(
            assessment_snapshot_id,
            limit,
            symbol=symbol,
        )

    async def evaluate_readiness(
        self,
        symbol: str,
        snapshot: ResearchAssessmentSnapshotData | None,
        *,
        outcome_horizon_key: str = DEFAULT_OUTCOME_HORIZON_KEY,
    ) -> CalibrationReadinessData:
        """Return corpus-gate readiness for ``symbol`` without persisting anything."""

        primary_horizon = normalize_outcome_horizon_key(outcome_horizon_key)
        by_horizon: list[CalibrationHorizonReadinessData] = []
        primary: CalibrationReadinessData | None = None
        for horizon in OUTCOME_HORIZON_KEYS:
            corpus = await self._corpus_reader.list_labeled_examples(
                symbol.upper(),
                self._corpus_limit,
                outcome_horizon_key=horizon,
            )
            readiness = evaluate_calibration_readiness(
                symbol,
                snapshot,
                corpus,
                min_corpus=self._min_corpus,
                min_bucket=self._min_bucket,
                index_bucket_width=self._index_bucket_width,
                outcome_horizon_key=horizon,
            )
            by_horizon.append(
                CalibrationHorizonReadinessData(
                    outcome_horizon_key=horizon,
                    status=readiness.status,
                    corpus_count=readiness.corpus_count,
                    bucket_count=readiness.bucket_count,
                    detail=readiness.detail,
                )
            )
            if horizon == primary_horizon:
                primary = readiness

        assert primary is not None
        result = CalibrationReadinessData(
            symbol=primary.symbol,
            status=primary.status,
            assessment_snapshot_id=primary.assessment_snapshot_id,
            research_index=primary.research_index,
            corpus_count=primary.corpus_count,
            bucket_count=primary.bucket_count,
            min_corpus=primary.min_corpus,
            min_bucket=primary.min_bucket,
            index_bucket_width=primary.index_bucket_width,
            calibration_method_id=primary.calibration_method_id,
            detail=primary.detail,
            outcome_horizon_key=primary.outcome_horizon_key,
            by_horizon=tuple(by_horizon),
        )
        logger.info(
            "research_calibration_readiness_evaluated",
            extra={
                "symbol": result.symbol,
                "status": result.status.value,
                "outcome_horizon_key": result.outcome_horizon_key,
                "corpus_count": result.corpus_count,
                "bucket_count": result.bucket_count,
            },
        )
        return result


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
