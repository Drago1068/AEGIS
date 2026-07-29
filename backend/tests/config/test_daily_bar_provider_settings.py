"""Unit tests for settings validation of daily-bar provider selection."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from aegis.config.settings import Settings


def test_secondary_may_be_unset() -> None:
    settings = Settings(environment="test", daily_bar_primary_source="polygon")
    assert settings.daily_bar_primary_source == "polygon"
    assert settings.daily_bar_secondary_source is None


def test_empty_secondary_becomes_none() -> None:
    settings = Settings(
        environment="test",
        daily_bar_primary_source="alpha_vantage",
        daily_bar_secondary_source="",  # type: ignore[arg-type]
    )
    assert settings.daily_bar_secondary_source is None


def test_secondary_must_differ_from_primary() -> None:
    with pytest.raises(ValidationError, match="SECONDARY_SOURCE must differ"):
        Settings(
            environment="test",
            daily_bar_primary_source="polygon",
            daily_bar_secondary_source="polygon",
        )


def test_primary_and_secondary_pair_accepted() -> None:
    settings = Settings(
        environment="test",
        daily_bar_primary_source="alpha_vantage",
        daily_bar_secondary_source="polygon",
    )
    assert settings.daily_bar_secondary_source == "polygon"
