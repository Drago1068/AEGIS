# ADR-0114: Phase 113 Outcome-Label Action Aria Includes Load Kind

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 89–111 name compute/download outcome-label actions with the active assessment id.
When the panel is on scan-labeled (or latest) history, screen-reader users still only hear
the numeric id and must infer load-kind from the caption.

## Decisions

### 1. Console

When ``outcomeLabelHistoryLoadKind`` is set, append `` (scan-labeled)`` or `` (latest)`` to
compute and download outcome-label ``aria-label`` strings. Visible button text/id chip
unchanged. No API changes.

### 2. Out of scope

Changing calibration aria labels, default-on calibration, orders, ACME.

## Related documents

- [0112-phase-111-resolve-outcome-label-history-load-kind.md](0112-phase-111-resolve-outcome-label-history-load-kind.md)
- [0115-phase-114-nas-live-verify-phase-113.md](0115-phase-114-nas-live-verify-phase-113.md)
