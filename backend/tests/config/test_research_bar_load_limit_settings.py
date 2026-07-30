"""Settings tests for Phase 51 research bar load limit (ADR-0052)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from aegis.config.settings import Settings


def test_research_bar_load_limit_default() -> None:
    settings = Settings(environment="test")
    assert settings.research_bar_load_limit == 252


def test_research_bar_load_limit_bounds() -> None:
    assert Settings(environment="test", research_bar_load_limit=40).research_bar_load_limit == 40
    assert (
        Settings(environment="test", research_bar_load_limit=2000).research_bar_load_limit
        == 2000
    )
    with pytest.raises(ValidationError):
        Settings(environment="test", research_bar_load_limit=39)
    with pytest.raises(ValidationError):
        Settings(environment="test", research_bar_load_limit=2001)
