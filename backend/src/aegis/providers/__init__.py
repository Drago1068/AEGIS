"""Typed interfaces and adapters for external market data providers.

Domain code depends on the interfaces defined here, never on a concrete provider SDK, so
providers can be swapped or faked in tests. Adapters preserve raw provenance needed for
audits and must reject invalid, stale, zero, negative, closed-session, or otherwise unusable
quotes before any derived metric is computed (see
``docs/architecture/market-data-contracts.md``).

Phase 0 note: no provider adapters are implemented yet; this package is an intentionally
empty placeholder for the module boundary.
"""
