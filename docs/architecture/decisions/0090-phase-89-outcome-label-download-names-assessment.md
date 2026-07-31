# ADR-0090: Phase 89 Outcome-Label Download Names Assessment Id

- Status: Accepted
- Date: 2026-07-30

## Context

Phase 87 binds download to the loaded assessment id (ADR-0088). Operators still see a
generic button label and cannot tell which assessment will be exported without reading
the panel caption.

## Decisions

### 1. Console

When a download target assessment id is known (``outcomeLabelHistoryAssessmentId`` or
``latest.id``), the download control:

- Shows ``({id})`` after the button text
- Sets ``aria-label`` to ``Download outcome labels JSON for assessment {id}``
- Exposes ``data-testid="download-outcome-labels"``

### 2. Out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders, ACME.

## Related documents

- [0088-phase-87-outcome-label-download-loaded-assessment.md](0088-phase-87-outcome-label-download-loaded-assessment.md)
- [0089-phase-88-nas-live-verify-phase-87.md](0089-phase-88-nas-live-verify-phase-87.md)
