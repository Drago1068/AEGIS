# ADR-0009: Phase 8 Scheduled Research Assessments After Ingest

- Status: Accepted
- Date: 2026-07-28

## Context

Phases 0–7 delivered foundation through NAS packaging, including Phase 6 on-demand
research-only assessments (`daily_bar_research_v1`) and Phase 2 locked scheduled ingestion.
Operators still had to request assessments manually after bars landed. Phase 8 automates
research after successful ingest without adding calibration, actionable promotion, orders,
TLS termination, or NAS live-verify work.

## Decisions

### 1. Scope

After each successful locked scheduled ingest cycle—and after each successful on-demand
`POST /market-data/ingest` when the same flag is enabled—run Phase 6
`daily_bar_research_v1` for every active watchlist symbol. Persist append-only snapshots on
success; on fail-closed gates, skip with structured logs and **no row**. Keep
`state=research_only`, coverage set, `probability_confidence=null`. No new scoring method.

### 2. Domain orchestration (Protocol-based)

`aegis.domain.scheduled_research.run_research_after_ingest(symbols, service)` assesses
symbols one-by-one via a `ResearchAssessor` Protocol (satisfied by
`ResearchAssessmentService`). Per-symbol try/fail-closed: a gate failure or unexpected error
skips that symbol and continues the batch. Domain code stays free of APScheduler and Redis
concretes.

### 3. Single settings flag

`AEGIS_RESEARCH_SCHEDULE_AFTER_INGEST_ENABLED` controls **both**:

- post-ingest research after a successful **locked scheduled** cycle; and
- post-ingest research after a successful **on-demand** `POST /market-data/ingest`.

When false, Phase 6 on-demand `POST /research/{symbol}/assessments` is unchanged. One flag
avoids divergent scheduled vs manual-ingest behavior.

| Environment | Default | Rationale |
| --- | --- | --- |
| Local / Settings default | `true` | Nightly and manual ingest both refresh research snapshots during development. |
| NAS / prod-leaning (`.env.nas.example`) | `true` | Same automation after scheduled ingest on the NAS stack. |

Operators who want ingest without automatic assessments set the flag to `false`.

### 4. Locking: research inside the ingest lock

**Chosen option:** run research **inside the same Redis lock** as scheduled ingest, after
ingest succeeds and **before** releasing the lock.

- Prevents overlapping scheduled cycles from double-ingesting and double-assessing.
- Avoids a second lock key and release-then-reacquire races.
- Lock TTL (`AEGIS_INGESTION_SCHEDULE_LOCK_TTL_SECONDS`) must cover ingest **plus** research.

On-demand ingest does not acquire the scheduled lock (unchanged from Phase 2). When the flag
is enabled, on-demand post-ingest research runs sequentially after that request’s ingest
completes. Concurrent on-demand vs scheduled overlap remains the same class of race as
pre-Phase-8 on-demand ingest; the scheduled path remains single-flight via the lock.

### 5. Stored bars only

Post-ingest research uses the existing bar reader / snapshot store path only. No extra
provider calls.

### 6. Operator visibility

No new persistence table or run-summary API. Structured logs
(`research_after_ingest_skipped`, `research_after_ingest_completed`) plus existing
append-only snapshots and the symbol-page research panel (RESEARCH ONLY labels; copy notes
that post-ingest snapshots may appear after ingest). Refresh latest to load the newest row.

## Consequences

- Scheduled and on-demand ingest can refresh research snapshots automatically when enabled.
- Fail-closed gates are unchanged; skips never invent or persist partial assessments.
- Calibration, actionable promotion, recommendations, chart signals, and orders remain out of
  scope.

## Explicitly out of scope

- Calibration / non-null `probability_confidence`
- Actionable promotion, recommendations, chart signals
- Order placement or transmission
- TLS termination changes
- NAS live verify (package/deploy/verify scripts unchanged in purpose)

## Related documents

- [0003-phase-2-scheduled-watchlist.md](0003-phase-2-scheduled-watchlist.md)
- [0007-phase-6-research-only-scoring.md](0007-phase-6-research-only-scoring.md)
- [0008-phase-7-nas-deployment.md](0008-phase-7-nas-deployment.md)
- [../overview.md](../overview.md)
- [../../operations/configuration.md](../../operations/configuration.md)
