# ADR-0307: Phase 306 NAS Live Verification of Phase 305

- Status: Accepted
- Date: 2026-08-01

## Context

Phase 305 defaulted assessment history to distinct-as_of rows with optional show-all
(ADR-0306). Operators needed a verified frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``HEAD`` ``9413364`` via ``git archive``; preserved ``.env.nas``;
   rebuilt frontend TLS; waited ``/ready`` via docker-exec urllib.
2. ``verify.ps1`` passed. Live AAPL: ``list_count=100`` ``distinct_as_of=75``
   ``hidden_duplicates=25``.
3. Alembic ``0009`` / ``head``.

### 2. Upload ≠ verified

Retain live verify stdout as evidence.

## Related documents

- [0306-phase-305-distinct-as-of-assessment-history.md](0306-phase-305-distinct-as-of-assessment-history.md)
- [0308-phase-307-labeling-frontier-readout.md](0308-phase-307-labeling-frontier-readout.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
