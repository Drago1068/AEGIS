# ADR-0279: Phase 278 NAS Live Verification of Phase 277

- Status: Accepted
- Date: 2026-07-31

## Context

Phase 277 surfaced ``primary_fetch_fallback`` on the operator IngestPanel (ADR-0278).
Operators needed a verified frontend redeploy under lab TLS.

## Decisions

### 1. Scope completed

1. Deployed ``99b5032`` TLS; rebuilt frontend.
2. ``verify.ps1`` passed; alembic ``0009`` / ``head``.
3. Live ingest still reports ``primary_fetch_fallback=full_to_compact`` (Phase 276 log).
   UI column covered by unit tests; frontend reachability ``200|307``.

### 2. Upload ≠ verified

Retain verify stdout as acceptance evidence.

## Related documents

- [0278-phase-277-ingest-ui-primary-fetch-fallback.md](0278-phase-277-ingest-ui-primary-fetch-fallback.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
