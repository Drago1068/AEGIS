# ADR-0269: Phase 268 NAS Live Verification of Phase 267

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 267 resolved mixed label bar source in evidence-summary with stored bars
(ADR-0268). Operators needed a verified backend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``7a55d7b`` TLS; rebuilt backend.
2. ``verify.ps1`` passed; alembic ``0009`` / ``head``.
3. Live AAPL evidence-summary:
   ``component_source=mixed``, ``latest_resolved_label_bar_source=polygon``
   (concrete; no longer opaque ``mixed``).

### 2. Upload ≠ verified

Retain verify stdout as acceptance evidence.

## Related documents

- [0268-phase-267-resolve-mixed-label-bar-source-evidence.md](0268-phase-267-resolve-mixed-label-bar-source-evidence.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
