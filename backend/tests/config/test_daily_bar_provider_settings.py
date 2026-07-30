"""Unit tests for settings validation of daily-bar provider selection."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from aegis.config.settings import Settings


def test_daily_bar_output_size_default_full(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AEGIS_DAILY_BAR_OUTPUT_SIZE", raising=False)
    settings = Settings(_env_file=None, environment="test")
    assert settings.daily_bar_output_size == "full"


def test_daily_bar_output_size_compact_still_allowed() -> None:
    settings = Settings(
        _env_file=None,
        environment="test",
        daily_bar_output_size="compact",
    )
    assert settings.daily_bar_output_size == "compact"


def test_secondary_may_be_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AEGIS_DAILY_BAR_SECONDARY_SOURCE", raising=False)
    settings = Settings(
        _env_file=None,
        environment="test",
        daily_bar_primary_source="polygon",
    )
    assert settings.daily_bar_primary_source == "polygon"
    assert settings.daily_bar_secondary_source is None


def test_empty_secondary_becomes_none() -> None:
    settings = Settings(
        _env_file=None,
        environment="test",
        daily_bar_primary_source="alpha_vantage",
        daily_bar_secondary_source="",  # type: ignore[arg-type]
    )
    assert settings.daily_bar_secondary_source is None


def test_secondary_must_differ_from_primary() -> None:
    with pytest.raises(ValidationError, match="SECONDARY_SOURCE must differ"):
        Settings(
            _env_file=None,
            environment="test",
            daily_bar_primary_source="polygon",
            daily_bar_secondary_source="polygon",
        )


def test_primary_and_secondary_pair_accepted() -> None:
    settings = Settings(
        _env_file=None,
        environment="test",
        daily_bar_primary_source="alpha_vantage",
        daily_bar_secondary_source="polygon",
    )
    assert settings.daily_bar_secondary_source == "polygon"
