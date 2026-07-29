"""Settings tests for Phase 15 research calibration flags."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from aegis.config.settings import Settings


def test_research_calibration_defaults() -> None:
    settings = Settings(environment="test")
    assert settings.research_calibration_after_label_enabled is False
    assert settings.research_calibration_min_corpus == 10
    assert settings.research_calibration_min_bucket == 5
    assert settings.research_calibration_index_bucket_width == pytest.approx(0.15)


def test_research_calibration_min_corpus_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="test", research_calibration_min_corpus=0)
