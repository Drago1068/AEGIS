"""Settings tests for Phase 11 multi-source research coverage flags."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from aegis.config.settings import Settings


def test_multi_source_research_defaults() -> None:
    settings = Settings(_env_file=None, environment="test")
    assert settings.research_multi_source_coverage_enabled is True
    assert settings.research_multi_source_close_tolerance == pytest.approx(0.002)
    assert settings.research_multi_source_disagreement_fail_closed is False
    assert settings.research_allow_cross_source_component_fill is True


def test_multi_source_close_tolerance_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, environment="test", research_multi_source_close_tolerance=0)
