"""Typed interfaces and adapters for external market data providers.

Domain code depends on the interfaces defined here, never on a concrete provider SDK, so
providers can be swapped or faked in tests. Adapters preserve raw provenance needed for
audits and must reject invalid, stale, zero, negative, closed-session, or otherwise unusable
quotes before any derived metric is computed (see
``docs/architecture/market-data-contracts.md``).

Concrete adapters: Alpha Vantage (``alpha_vantage``) and Polygon.io (``polygon``). Selection
and optional failover are configuration-driven (ADR-0011).
"""
