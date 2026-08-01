# ADR-0268: Phase 267 Resolve Mixed Label Bar Source in Evidence Summary

- Status: Accepted
- Date: 2026-07-31

## Context

Phases 265–266 closed primary-vs-winning tip attribution. Live AAPL evidence-summary still
reported ``latest_resolved_label_bar_source=mixed`` for the latest mixed assessment even
though as-of provenance can pick a concrete source (Phase 65 / ADR-0066 for labeling).
Operators cannot tell which source would be used for forward closes without a DB inspect.

Prefer fixing evidence-summary source resolution (pass bars into
``resolve_label_bar_source``) over another tip scalar or UI modularization.

## Decisions

### 1. Resolve mixed with bars

When building evidence-summary for the latest assessment, resolve
``latest_resolved_label_bar_source`` with loaded bars so true-mixed rows get a concrete
source when as-of closes exist (same rules as ADR-0066). Keep ``mixed`` only when no
usable as-of close resolves. Never invent sources or closes.

``OutcomeLabelService.resolve_label_bar_source_for_assessment`` loads bars and calls
``resolve_label_bar_source(snapshot, bars)``. Persisted ``label.bar_source`` still wins
when the latest assessment is already labeled.

### 2. Out of scope

Inventing closes, changing assessment ``input_source``, calibration, orders.

### 3. Why this next

Tip diagnostics are solid; remaining operator gap is opaque ``mixed`` label bar source on
the latest assessment.

## Consequences

- Evidence-summary surfaces a concrete label bar source for unlabeled mixed assessments
  when as-of closes exist.
- Fail-closed: unresolved mixed remains ``mixed``.
- Phase 268 live-verifies under lab TLS.

## Related documents

- [0066-phase-65-prefer-mixed-label-backfill.md](0066-phase-65-prefer-mixed-label-backfill.md)
- [0267-phase-266-nas-live-verify-phase-265.md](0267-phase-266-nas-live-verify-phase-265.md)
- [0269-phase-268-nas-live-verify-phase-267.md](0269-phase-268-nas-live-verify-phase-267.md)
