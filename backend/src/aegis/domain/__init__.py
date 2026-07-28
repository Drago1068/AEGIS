"""Framework-free business rules and orchestration.

This package must not import FastAPI, SQLAlchemy sessions, or provider SDKs directly; it
depends only on repository and provider interfaces defined in ``persistence`` and
``providers``, so domain rules can be tested and reasoned about independently of
infrastructure.

Phase 0 note: this package contains no domain logic. Scoring, recommendation, prediction, and
trading logic are added only in later phases once their evidence gates are satisfied, per the
project rules.
"""
