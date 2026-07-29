"""Typed provider-adapter error hierarchy.

Provider adapters must raise these instead of returning empty/partial results when an
external provider signals an error, so an ingestion caller can never mistake "the provider
rejected this request" for "the provider has no data."
"""

from __future__ import annotations


class ProviderError(Exception):
    """A provider returned an error, or its response could not be interpreted safely.

    Covers malformed payloads, HTTP-level failures, and providers that report an error inside
    an otherwise-successful HTTP response (for example Alpha Vantage's ``200 OK`` responses
    that carry an ``Error Message`` field instead of data).
    """


class ProviderRateLimitError(ProviderError):
    """The provider reported that a rate limit (or a premium-tier gate) was hit.

    Kept distinct from :class:`ProviderError` so callers can choose to back off, skip the
    remaining watchlist for this run, or surface a more specific message, without parsing
    exception text. Eligible for configured secondary failover (see ADR-0011).
    """


class ProviderUnavailableError(ProviderError):
    """The provider could not be reached or returned a transient infrastructure failure.

    Covers missing credentials at call time, transport failures, and HTTP 5xx responses.
    Kept distinct so ingestion can fail over to a secondary adapter without treating
    malformed payloads or invalid-symbol answers as failover triggers (ADR-0011).
    """
