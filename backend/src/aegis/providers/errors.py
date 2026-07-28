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
    exception text.
    """
