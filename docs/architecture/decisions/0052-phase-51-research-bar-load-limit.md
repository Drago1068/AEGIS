# ADR-0052: Phase 51 Configurable Research Bar Load Limit

- Status: Accepted
- Date: 2026-07-30

## Context

Assessment and outcome-label paths load a fixed ``BAR_LOAD_LIMIT`` of 120 recent daily bars.
Live Phase 50 evidence showed AAPL saturated that window (~40 assessments, no remaining
unlabeled label-ready candidates). Operators need a single configuration knob to load deeper
history for on-demand assess, assessment backfill, and outcome-label backfill without
hardcoding a new constant.

## Decisions

### 1. Setting

Add ``AEGIS_RESEARCH_BAR_LOAD_LIMIT`` (Pydantic ``research_bar_load_limit``):

- Default: **252** (~one NYSE trading year) so fresh deploys can grow corpora past 120.
- Bounds: ``ge=40`` (enough for lookback 20 + forward 20), ``le=2000``.
- Shared by:
  - ``ResearchAssessmentService.assess`` and ``backfill_assessments``
  - ``OutcomeLabelService`` (label compute + Phase 49 backfill candidate readiness)

### 2. Domain constant

Keep ``BAR_LOAD_LIMIT = 120`` as the historical module default for constructor fallbacks and
tests that omit the setting. Wired services always pass the settings value.

### 3. Existing-assessment scan

Assessment backfill expands the existing as-of lookup to at least ``bar_load_limit`` so
deeper candidates are not re-inserted when prior rows fall outside a small list window.

### 4. Out of scope

- Guaranteeing readiness ``ready`` / fixing ``insufficient_similar_examples``
- Changing ingest ``outputsize`` / provider history depth
- Auto-chaining assessment → label backfill
- Default-on calibration, actionable promotion, orders, ACME

## Related documents

- [0048-phase-47-label-ready-assessment-backfill.md](0048-phase-47-label-ready-assessment-backfill.md)
- [0050-phase-49-prefer-unlabeled-label-backfill.md](0050-phase-49-prefer-unlabeled-label-backfill.md)
- [0051-phase-50-nas-live-verify-phase-49.md](0051-phase-50-nas-live-verify-phase-49.md)
- [../../operations/configuration.md](../../operations/configuration.md)
