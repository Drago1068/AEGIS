"""Application settings sourced exclusively from environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    watchlist_symbols: str = Field(
        default="AAPL,MSFT,SPY",
        description=(
            "Comma-separated bootstrap seed symbols. Only used to seed the database-backed "
            "watchlist (`watchlist_symbols` table) the first time it is empty; once any row "
            "exists, this value is never read again. See ADR-0003."
        ),
    )
    daily_bar_output_size: Literal["compact", "full"] = Field(
        default="compact",
        description=(
            "Alpha Vantage 'outputsize' parameter: 'compact' returns the latest ~100 daily "
            "bars, 'full' returns the full available history."
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
            "process can hold the lock; must comfortably exceed a normal run's duration."
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
