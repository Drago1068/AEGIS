"""Framework-free business rules and orchestration.

This package must not import FastAPI, SQLAlchemy sessions, or provider SDKs directly; it
depends only on repository and provider interfaces defined in ``persistence`` and
``providers``, so domain rules can be tested and reasoned about independently of
infrastructure.

Phase 6 adds research-only assessment foundations (``research_assessment``). Recommendation,
prediction, actionable promotion, and trading/order logic remain out of scope until their
evidence gates are satisfied.
"""
