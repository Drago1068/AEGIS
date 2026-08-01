# ADR-0308: Phase 307 Labeling Frontier Readout

- Status: Accepted
- Date: 2026-08-01

## Context

Phases 283–306 elevated labeling diagnostics and assessment history/charts. Live AAPL
remains tip-not-ready (``forward_bar_shortfall=20``, ``required_label_end_date=2026-08-28``,
min-horizon unlock ``2026-08-07``). Operators must scan several callout/dl fields to answer
“when can the tip label?” Calendar-bound progress is the next product gap — not more
history polish.

Prefer a compact research-only frontier readout from existing evidence-summary fields
(shortfall, required end, min-horizon counterparts, last available bar date). No new API
scalars; never invent closes.

## Decisions

### 1. Labeling frontier readout

Add a research-only strip above labeling-diagnostics that surfaces tip labeling unlock
dates/shortfalls from fields already on evidence-summary
(``latest_assessment_is_label_ready``, ``latest_assessment_forward_bar_shortfall``,
``latest_assessment_required_label_end_date``, min-horizon shortfall/end,
``latest_assessment_last_available_label_bar_date``). Keep fail-closed wording (not a
signal). Leave callouts unchanged.

### 2. Out of scope

Live orders, inventing bars/labels, auto-labeling when ready, calibration default-on,
additional charts, new API scalars.

## Related documents

- [0307-phase-306-nas-live-verify-phase-305.md](0307-phase-306-nas-live-verify-phase-305.md)
- [0309-phase-308-nas-live-verify-phase-307.md](0309-phase-308-nas-live-verify-phase-307.md)
