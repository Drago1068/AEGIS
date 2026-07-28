"""HTTP interface layer.

This package contains FastAPI routers, request/response Pydantic schemas, and HTTP-specific
error mapping. It contains no business logic; it delegates to ``domain`` (once domain logic
exists in a later phase). Phase 0 exposes only process liveness (``/health``) and readiness
(``/ready``) endpoints.
"""
