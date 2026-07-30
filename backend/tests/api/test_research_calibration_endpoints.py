"""API tests for on-demand research probability calibration endpoints (Phase 18/19)."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from httpx import ASGITransport, AsyncClient

from aegis.api.dependencies import get_research_calibration_service, require_operator
from aegis.api.main import create_app
from aegis.config.settings import Settings
from aegis.domain.research_probability_calibration import (
    CALIBRATION_METHOD_ID,
    CalibrationReason,
    CalibrationUnavailableError,
    ProbabilityCalibrationData,
)
from aegis.persistence.models import Operator


def _operator() -> Operator:
    return Operator(
        id=1,
        username="operator",
        password_hash="unused",
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        updated_at=datetime(2024, 1, 1, tzinfo=UTC),
    )


def _calibration() -> ProbabilityCalibrationData:
    return ProbabilityCalibrationData(
        id=7,
        assessment_snapshot_id=99,
        symbol="AAPL",
        calibration_method_id=CALIBRATION_METHOD_ID,
        calibration_method_version=1,
        state="research_only",
        computed_at=datetime(2024, 1, 26, 18, 0, tzinfo=UTC),
        probability_confidence=0.6,
        corpus_count=12,
        bucket_count=8,
        schema_version=1,
    )


class _FakeCalibrationService:
    def __init__(
        self,
        *,
        on_calibrate: ProbabilityCalibrationData | Exception | None = None,
        latest: ProbabilityCalibrationData | None = None,
        listed: list[ProbabilityCalibrationData] | None = None,
    ) -> None:
        self._on_calibrate = on_calibrate
        self._latest = latest
        self._listed = listed or []
        self.calibrate_calls: list[tuple[str, int]] = []
        self.list_calls: list[tuple[str, int, int]] = []

    async def calibrate_assessment(
        self, symbol: str, assessment_snapshot_id: int
    ) -> ProbabilityCalibrationData:
        self.calibrate_calls.append((symbol, assessment_snapshot_id))
        if isinstance(self._on_calibrate, Exception):
            raise self._on_calibrate
        assert isinstance(self._on_calibrate, ProbabilityCalibrationData)
        return self._on_calibrate

    async def latest_calibration_for_assessment(
        self, assessment_snapshot_id: int
    ) -> ProbabilityCalibrationData | None:
        return self._latest

    async def list_calibrations_for_assessment(
        self,
        symbol: str,
        assessment_snapshot_id: int,
        limit: int,
    ) -> list[ProbabilityCalibrationData]:
        self.list_calls.append((symbol, assessment_snapshot_id, limit))
        return self._listed[:limit]


def _client(service: _FakeCalibrationService) -> AsyncClient:
    app = create_app(settings=Settings(environment="test", ingestion_schedule_enabled=False))
    app.dependency_overrides[require_operator] = _operator
    app.dependency_overrides[get_research_calibration_service] = lambda: service
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


async def test_post_calibration_returns_payload() -> None:
    calibration = _calibration()
    service = _FakeCalibrationService(on_calibrate=calibration)

    async with _client(service) as client:
        response = await client.post("/research/AAPL/assessments/99/calibrations")

    assert response.status_code == 200
    body = response.json()
    assert body["calibration_method_id"] == CALIBRATION_METHOD_ID
    assert body["probability_confidence"] == 0.6
    assert body["state"] == "research_only"
    assert service.calibrate_calls == [("AAPL", 99)]


async def test_post_calibration_422_on_fail_closed() -> None:
    service = _FakeCalibrationService(
        on_calibrate=CalibrationUnavailableError(
            CalibrationReason.INSUFFICIENT_LABELED_CORPUS,
            "need at least 10 labeled historical examples, found 3",
        )
    )

    async with _client(service) as client:
        response = await client.post("/research/AAPL/assessments/99/calibrations")

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["reason"] == "insufficient_labeled_corpus"


async def test_get_latest_calibration() -> None:
    calibration = _calibration()
    service = _FakeCalibrationService(latest=calibration)

    async with _client(service) as client:
        response = await client.get("/research/AAPL/assessments/99/calibrations/latest")

    assert response.status_code == 200
    assert response.json()["assessment_snapshot_id"] == 99


async def test_get_latest_calibration_404() -> None:
    service = _FakeCalibrationService(latest=None)

    async with _client(service) as client:
        response = await client.get("/research/AAPL/assessments/99/calibrations/latest")

    assert response.status_code == 404


async def test_list_calibrations_newest_first() -> None:
    newer = _calibration()
    older = replace(
        newer,
        id=6,
        computed_at=datetime(2024, 1, 25, 18, 0, tzinfo=UTC),
        probability_confidence=0.55,
    )
    service = _FakeCalibrationService(listed=[newer, older])

    async with _client(service) as client:
        response = await client.get("/research/AAPL/assessments/99/calibrations?limit=10")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["id"] == 7
    assert body[1]["id"] == 6
    assert body[0]["state"] == "research_only"
    assert service.list_calls == [("AAPL", 99, 10)]


async def test_list_calibrations_empty() -> None:
    service = _FakeCalibrationService(listed=[])

    async with _client(service) as client:
        response = await client.get("/research/AAPL/assessments/99/calibrations")

    assert response.status_code == 200
    assert response.json() == []
