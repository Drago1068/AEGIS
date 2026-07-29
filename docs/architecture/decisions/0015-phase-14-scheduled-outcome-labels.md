# ADR-0015: Phase 14 Scheduled Outcome Labels After Research Assessments

- Status: Accepted
- Date: 2026-07-29

## Context

Phase 13 added on-demand `forward_total_return_v1` outcome labels linked to research assessment
snapshots. Operators still had to trigger labeling manually after each assessment. Phase 14
automates labeling after successful assessments without adding calibration,
`probability_confidence`, actionable promotion, or orders.

## Decisions

### 1. Scope

After each successful research assessment—from post-ingest research (Phase 8) or from on-demand
`POST /research/{symbol}/assessments` when the flag is enabled—attempt Phase 13
`forward_total_return_v1` labeling. Persist append-only label rows on success; on fail-closed
gates (e.g. insufficient forward bars), skip with structured logs and **no row**. Keep
`state=research_only` on labels; assessments keep `probability_confidence=null`. No new label
math.

### 2. Domain orchestration (Protocol-based)

`aegis.domain.scheduled_outcome_labels.run_outcome_labels_after_assessments` labels assessments
one-by-one via an `OutcomeLabeler` Protocol (satisfied by `OutcomeLabelService`). Per-assessment
try/fail-closed: a gate failure or unexpected error skips that assessment and continues the
batch. `run_outcome_labels_after_research` maps a Phase 8 `ResearchAfterIngestSummary` (with
persisted `assessment_snapshot_id` values) into that batch. Domain code stays free of
APScheduler and Redis concretes.

### 3. Single settings flag

`AEGIS_RESEARCH_OUTCOME_LABEL_AFTER_ASSESSMENT_ENABLED` controls **both**:

- outcome labeling after successful assessments from **post-ingest research** (when Phase 8
  research is also enabled); and
- outcome labeling after a successful **on-demand**
  `POST /research/{symbol}/assessments`.

When false, Phase 13 on-demand `POST .../outcome-labels` is unchanged. On-demand assessment
responses still succeed even when labeling skips (fail-closed skip only).

| Environment | Default | Rationale |
| --- | --- | --- |
| Local / Settings default | `true` | Labels accumulate automatically as forward windows complete. |
| NAS / prod-leaning (`.env.nas.example`) | `true` | Same automation after scheduled ingest + research on the NAS stack. |

### 4. Locking: labels inside the ingest lock

**Chosen option:** run post-ingest outcome labeling **inside the same Redis lock** as scheduled
ingest, after post-ingest research succeeds and **before** releasing the lock (mirrors ADR-0009).

On-demand ingest and on-demand assessment do not acquire the scheduled lock. When enabled,
post-ingest labeling runs sequentially after that request's research pass completes.

### 5. Stored bars only

Automatic labeling uses the existing Phase 13 bar reader / label store path only. No extra
provider calls.

### 6. Operator visibility

No new persistence table or run-summary API. Structured logs
(`outcome_label_after_assessment_skipped`, `outcome_label_after_assessment_completed`) plus
existing append-only label rows and the symbol-page research panel (Phase 13 UI).

## Consequences

- Scheduled and on-demand paths can refresh outcome labels automatically when enabled and
  forward bars are available.
- Fail-closed gates are unchanged; skips never invent or persist partial labels.
- Calibration, actionable promotion, recommendations, and orders remain out of scope.

## Explicitly out of scope

- Non-null `probability_confidence` / calibration fitting
- Actionable promotion, recommendations, orders
- New label methods or horizons
- Portfolio or cross-symbol analytics
- Live NAS deployment

## Related documents

- [0014-phase-13-research-outcome-labels.md](0014-phase-13-research-outcome-labels.md)
- [0009-phase-8-scheduled-research.md](0009-phase-8-scheduled-research.md)
- [../overview.md](../overview.md)
- [../../operations/configuration.md](../../operations/configuration.md)
