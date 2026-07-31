# ADR-0160: Phase 159 Evidence Summary Latest Method Version

- Status: Proposed
- Date: 2026-07-31

## Context

Evidence summary now exposes top-level ``latest_method_id`` for the latest assessment.
Operators still dig into nested ``latest_assessment.method_version`` to confirm which
method revision produced the snapshot. Pairing version with method id completes method
provenance without inventing values.

## Decisions

### 1. API

Add ``latest_method_version: int | null`` to ``ResearchEvidenceSummaryResponse`` (+ export).
Copy from ``latest_assessment.method_version`` when present; otherwise null. Never invent.
``ge=1`` when set (matches assessment schema).

### 2. Console

Show the field on ``ResearchEvidenceSummarySection`` near ``latest_method_id``
(``data-testid="evidence-latest-method-version"``).

### 3. Out of scope

New scoring math, default-on calibration, orders, ACME, UI structural extracts.

## Related documents

- [0158-phase-157-evidence-summary-latest-method-id.md](0158-phase-157-evidence-summary-latest-method-id.md)
- [0161-phase-160-nas-live-verify-phase-159.md](0161-phase-160-nas-live-verify-phase-159.md)
