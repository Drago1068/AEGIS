"""Application settings sourced exclusively from environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Final, Literal, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DailyBarSourceId = Literal["alpha_vantage", "polygon"]
DAILY_BAR_SOURCE_IDS: Final[tuple[DailyBarSourceId, ...]] = ("alpha_vantage", "polygon")


class Settings(BaseSettings):
    """Runtime configuration for the AEGIS backend service.

    Every field is sourced from an environment variable (optionally via a local ``.env``
    file during development). No field has a production-usable hardcoded default for
    secrets, hostnames, or credentials; the development defaults below are placeholders
    documented in ``.env.example`` and ``docs/operations/configuration.md``.
    """

    model_config = SettingsConfigDict(
        env_prefix="AEGIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "test", "ci", "production"] = "development"

    database_url: str = Field(
        default="postgresql+asyncpg://aegis:aegis@localhost:5432/aegis",
        description="SQLAlchemy async connection string for PostgreSQL/TimescaleDB.",
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Connection string for Redis.",
    )

    readiness_timeout_seconds: float = Field(
        default=2.0,
        gt=0,
        description="Maximum time to wait for a single dependency check in /ready.",
    )

    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000, gt=0, lt=65536)

    cors_origins: str = Field(
        default="http://localhost:3000",
        description=(
            "Comma-separated browser origins allowed by CORSMiddleware. Required so the "
            "Phase 3 Next.js operator console can call the API from a different origin. "
            "See ADR-0004."
        ),
    )

    daily_bar_primary_source: DailyBarSourceId = Field(
        default="alpha_vantage",
        description=(
            "Primary daily-bar provider source id (`alpha_vantage` or `polygon`). "
            "See ADR-0011."
        ),
    )
    daily_bar_secondary_source: DailyBarSourceId | None = Field(
        default=None,
        description=(
            "Optional secondary daily-bar provider for failover on rate-limit or "
            "unavailable errors. Must differ from the primary when set. See ADR-0011."
        ),
    )

    alpha_vantage_api_key: str | None = Field(
        default=None,
        description=(
            "API key for Alpha Vantage. Optional so the service can start without it; "
            "ingestion fails with a clear error if it is unset when invoked."
        ),
    )
    alpha_vantage_base_url: str = Field(
        default="https://www.alphavantage.co/query",
        description="Base URL for the Alpha Vantage REST API.",
    )
    alpha_vantage_request_interval_seconds: float = Field(
        default=12.0,
        ge=0,
        description=(
            "Minimum delay between successive Alpha Vantage requests within one ingestion "
            "run, to stay within the provider's rate limit."
        ),
    )

    polygon_api_key: str | None = Field(
        default=None,
        description=(
            "API key for Polygon.io. Optional so the service can start without it; "
            "ingestion fails with a clear error if it is unset when that provider is "
            "invoked. Never logged."
        ),
    )
    polygon_base_url: str = Field(
        default="https://api.polygon.io",
        description="Base URL for the Polygon.io REST API (no trailing path).",
    )
    polygon_request_interval_seconds: float = Field(
        default=12.0,
        ge=0,
        description=(
            "Minimum delay between successive Polygon requests within one ingestion run "
            "(reserved for pacing; adapters do not sleep internally)."
        ),
    )

    watchlist_symbols: str = Field(
        default="AAPL,MSFT,SPY",
        description=(
            "Comma-separated bootstrap seed symbols. Only used to seed the database-backed "
            "watchlist (`watchlist_symbols` table) the first time it is empty; once any row "
            "exists, this value is never read again. See ADR-0003."
        ),
    )
    daily_bar_output_size: Literal["compact", "full"] = Field(
        default="full",
        description=(
            "Daily-bar lookback hint: for Alpha Vantage, the `outputsize` parameter "
            "(`compact` ≈ 100 bars, `full` = full history); for Polygon, calendar-day "
            "lookback windows documented in ADR-0011. Default `full` for research corpus "
            "growth (ADR-0054); set `compact` explicitly for light labs."
        ),
    )
    exchange_calendar_name: str = Field(
        default="NYSE",
        description="pandas-market-calendars calendar name used for trading-day validation.",
    )
    max_latest_bar_staleness_trading_days: int = Field(
        default=3,
        ge=0,
        description=(
            "Maximum number of exchange trading days the most recent bar in a provider "
            "response may lag behind the current trading day before it is treated as stale."
        ),
    )
    market_data_correction_price_epsilon: float = Field(
        default=1e-6,
        gt=0,
        description=(
            "Relative price tolerance for provider revision detection (ADR-0013). Incoming "
            "OHLC differing beyond this epsilon from the current stored bar triggers a "
            "correction row instead of a silent skip."
        ),
    )

    ingestion_schedule_enabled: bool = Field(
        default=True,
        description="Whether the in-process scheduler runs ingestion automatically. See ADR-0003.",
    )
    ingestion_cron: str = Field(
        default="0 22 * * 1-5",
        description=(
            "Standard 5-field cron expression (minute hour day month day-of-week, UTC) for "
            "the scheduled ingestion job. Default: 22:00 UTC on weekdays, after the US cash "
            "session closes."
        ),
    )
    ingestion_schedule_lock_key: str = Field(
        default="aegis:ingestion:scheduler:lock",
        description="Redis key used to ensure only one process runs a scheduled cycle at a time.",
    )
    ingestion_schedule_lock_ttl_seconds: int = Field(
        default=1800,
        gt=0,
        description=(
            "Redis lock TTL for a scheduled ingestion cycle. Bounds how long a crashed "
            "process can hold the lock; must comfortably exceed a normal run's duration "
            "(including optional post-ingest research when enabled; see ADR-0009)."
        ),
    )

    research_schedule_after_ingest_enabled: bool = Field(
        default=True,
        description=(
            "When true, after each successful locked scheduled ingest cycle and after each "
            "successful on-demand POST /market-data/ingest, run Phase 6 "
            "daily_bar_research_v1 for active watchlist symbols (stored bars only). When "
            "false, Phase 6 on-demand POST /research/{symbol}/assessments is unchanged. "
            "See ADR-0009."
        ),
    )

    research_outcome_label_after_assessment_enabled: bool = Field(
        default=True,
        description=(
            "When true, after each successful research assessment from post-ingest research "
            "(when enabled) or on-demand POST /research/{symbol}/assessments, attempt Phase "
            "13 forward_total_return_v1 outcome labels (stored bars only). Fail-closed skips "
            "log and persist nothing (e.g. insufficient forward bars). When false, Phase 13 "
            "on-demand POST .../outcome-labels is unchanged. See ADR-0015."
        ),
    )

    research_calibration_after_label_enabled: bool = Field(
        default=False,
        description=(
            "When true, after each successful research assessment (and after successful "
            "outcome labeling when that path is enabled), attempt Phase 15 "
            "research_calibration_v1 using stored labeled historical corpus. Fail-closed "
            "skips log and persist nothing. When false, assessments keep "
            "probability_confidence=null in API responses. See ADR-0016."
        ),
    )
    research_calibration_min_corpus: int = Field(
        default=10,
        ge=1,
        description=(
            "Minimum labeled historical assessments (excluding the target) required for "
            "research_calibration_v1. See ADR-0016."
        ),
    )
    research_calibration_min_bucket: int = Field(
        default=5,
        ge=1,
        description=(
            "Minimum labeled examples within the research_index similarity bucket required "
            "for research_calibration_v1. See ADR-0016."
        ),
    )
    research_calibration_index_bucket_width: float = Field(
        default=0.15,
        gt=0,
        description=(
            "Absolute research_index tolerance for the similarity bucket in "
            "research_calibration_v1. See ADR-0016."
        ),
    )
    research_bar_load_limit: int = Field(
        default=252,
        ge=40,
        le=2000,
        description=(
            "Maximum recent daily bars loaded for research assessment, assessment backfill, "
            "and outcome-label paths (including Phase 49 label-ready selection). Default 252 "
            "(~one trading year). See ADR-0052."
        ),
    )

    research_multi_source_coverage_enabled: bool = Field(
        default=True,
        description=(
            "When true, research assessments use method_version 2 multi-source coverage "
            "weighting (preferred-source components + availability/agreement factors). "
            "When false, preserve Phase 6 method_version 1 behavior. See ADR-0012."
        ),
    )
    research_multi_source_close_tolerance: float = Field(
        default=0.002,
        gt=0,
        description=(
            "Relative close tolerance for multi-source agreement: "
            "(max(closes)-min(closes))/max(closes) must be <= this value. See ADR-0012."
        ),
    )
    research_multi_source_disagreement_fail_closed: bool = Field(
        default=False,
        description=(
            "When true, fail closed if comparable multi-source agreement falls below the "
            "documented floor (0.80). When false, only the soft agreement factor applies. "
            "See ADR-0012."
        ),
    )
    research_allow_cross_source_component_fill: bool = Field(
        default=False,
        description=(
            "When false (default), component return/vol/index series require 20 usable "
            "primary-quality bars from AEGIS_DAILY_BAR_PRIMARY_SOURCE only. When true, "
            "missing dates may be filled from the secondary source (no OHLCV blend). "
            "See ADR-0012."
        ),
    )

    operator_username: str = Field(
        default="operator",
        description=(
            "Bootstrap operator username. Used only to seed the `operators` table when it is "
            "empty; see ADR-0005."
        ),
    )
    operator_password: str = Field(
        default="change-me-before-non-local-use",
        description=(
            "Bootstrap operator password (plaintext in env only for first seed). Hashed with "
            "Argon2 before storage; never logged. Change before any non-local exposure."
        ),
    )
    session_cookie_name: str = Field(
        default="aegis_session",
        description="Name of the httpOnly session cookie issued on login.",
    )
    session_ttl_seconds: int = Field(
        default=86400,
        gt=0,
        description="Redis TTL and cookie max-age for an operator session (seconds).",
    )
    session_cookie_secure: bool = Field(
        default=False,
        description=(
            "Whether the session cookie is marked Secure. Keep false for local http:// "
            "development; set true behind HTTPS in production."
        ),
    )

    @field_validator("daily_bar_secondary_source", mode="before")
    @classmethod
    def _empty_secondary_source_to_none(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @model_validator(mode="after")
    def _secondary_differs_from_primary(self) -> Self:
        if (
            self.daily_bar_secondary_source is not None
            and self.daily_bar_secondary_source == self.daily_bar_primary_source
        ):
            raise ValueError(
                "AEGIS_DAILY_BAR_SECONDARY_SOURCE must differ from "
                "AEGIS_DAILY_BAR_PRIMARY_SOURCE when set"
            )
        return self

    @property
    def watchlist_seed_symbols(self) -> list[str]:
        """Parsed, upper-cased, order-preserving, de-duplicated bootstrap seed symbols."""

        seen: dict[str, None] = {}
        for raw_symbol in self.watchlist_symbols.split(","):
            symbol = raw_symbol.strip().upper()
            if symbol:
                seen[symbol] = None
        return list(seen)

    @property
    def cors_origin_list(self) -> list[str]:
        """Parsed, order-preserving, de-duplicated CORS allow-list origins."""

        seen: dict[str, None] = {}
        for raw_origin in self.cors_origins.split(","):
            origin = raw_origin.strip()
            if origin:
                seen[origin] = None
        return list(seen)


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance.

    Cached because ``Settings`` re-reads the environment on construction; tests that need a
    different configuration should construct ``Settings(...)`` directly rather than mutating
    process environment variables after this cache is populated.
    """

    return Settings()
