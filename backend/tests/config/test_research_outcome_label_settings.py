"""Settings tests for Phase 14 post-assessment outcome label flag."""

from __future__ import annotations

from aegis.config.settings import Settings


def test_outcome_label_after_assessment_default_enabled() -> None:
    settings = Settings(environment="test")
    assert settings.research_outcome_label_after_assessment_enabled is True
