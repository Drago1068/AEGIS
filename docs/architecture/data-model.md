# Point-in-Time Data Model Conventions

These conventions apply to every market observation and evidence record stored by AEGIS.
Phase 0 itself created no such tables; it only enabled and verified the TimescaleDB extension
(see the Phase 0 baseline migration described in [overview.md](overview.md)). Phase 1 adds the
first table built to these conventions, `market_daily_bar_observations` (see
[decisions/0002-phase-1-market-data-ingestion.md](decisions/0002-phase-1-market-data-ingestion.md)).

## Append-only and versioned

- Observation and evidence tables are **append-only**. Rows are never updated in place to
  reflect new information; a new row with a later `observed_at`/`ingested_at` timestamp is
  inserted instead.
- Corrections are represented as new rows referencing the record they correct, never as an
  overwrite. Historical observations must never be altered to make later data appear as
  though it was known earlier.
- Every table that stores derived or ingested data carries a `schema_version` (or equivalent)
  column so historical rows remain interpretable as the schema evolves.

## Timestamped and provenance-aware

- All timestamps are stored in UTC (`timestamptz` in PostgreSQL).
- Every record distinguishes at least:
  - `event_time` (when the observation is true of the world, if known),
  - `ingested_at` (when AEGIS received/recorded it).
- Every record carries a `source` (provider identifier) and enough raw provenance (for
  example a raw payload reference or checksum) to support an audit trail back to the original
  provider response.
- Simulated, delayed, fallback, or incomplete data is labeled explicitly (for example a
  `data_quality` or `is_delayed`/`is_simulated` flag), never presented as equivalent to
  validated, live, primary-source data.

## Reproducibility

- Given a `source`, `event_time`, and `ingested_at` (or a snapshot identifier), any derived
  metric must be reproducible from the stored raw observation - derived values are not stored
  as the only copy of information needed to recompute them.

## Coverage confidence vs probability confidence

AEGIS keeps two distinct notions of confidence, which must never be merged into a single
number or conflated in the schema or the UI:

- **Coverage confidence**: how complete and reliable the *evidence gathering* was (for
  example: how many independent sources were checked, how recent the data is, whether
  required fields were present). This describes the quality of the inputs.
- **Probability confidence**: a calibrated estimate of how likely a domain conclusion is,
  produced by domain/analysis logic in a later phase. This describes the quality of the
  conclusion.

Any future table or API payload that reports both must use separate, clearly named fields
(for example `coverage_confidence` and `probability_confidence`), and no code may combine
them into one score without an explicit, documented methodology reviewed at that phase's
gate.

## Research-only vs actionable state

- Every evidence record and any future recommendation-adjacent record carries an explicit
  state flag distinguishing **research-only** material (informational, not vetted for
  decision use) from **actionable** material (has passed the validation, calibration, and
  quality gates required for its phase).
- Research-only records must never be surfaced or formatted in a way that implies they are
  actionable.
- Promoting a record from research-only to actionable requires passing that phase's
  documented evidence gate; it is never a default or implicit transition.

## Fail-closed behavior

- If validation, calibration, evidence, or quality gates are incomplete or ambiguous for a
  given record, the system fails closed: the record stays research-only (or is rejected
  outright per [market-data-contracts.md](market-data-contracts.md)), rather than defaulting
  to an optimistic or actionable state.
