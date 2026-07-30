# ADR-0023: Phase 22 Symbol Research Evidence Summary

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 6–21 deliver assessments, outcome labels, calibration, readiness diagnostics, and
append-only history lists as separate endpoints. Operators need a single read-only view of
research evidence for one symbol without client-side stitching or inventing confidence.

## Decisions

### 1. Summary route

Authenticated:

- `GET /research/{symbol}/evidence-summary` — aggregate **research-only** evidence for
  ``symbol``:
  - `latest_assessment` (enriched with latest calibration overlay when present, else null)
  - `calibration_readiness` (Phase 16 diagnostics; never invents probability)
  - `latest_outcome_label` / `latest_calibration` for the latest assessment id (or null)
  - `assessment_count`, `outcome_label_count`, `calibration_count` (non-negative; counts
    for assessments use up to 100 newest rows; label/calibration counts are for the latest
    assessment id, up to 100 newest rows)
  - `state` always `research_only`
  - `detail` human-readable disclaimer

Empty / missing pieces use **null** or **0**. HTTP **200** even when no assessment exists.
Do not invent `probability_confidence` or label values.

### 2. Composition only

No new persistence tables or calibration/label methods. Reuse existing services and
repositories. No client-side research math.

### 3. Frontend

Operator console may show a compact evidence-summary section for the current symbol.

## Consequences

- One authenticated call gives an audit-friendly snapshot of research evidence.
- Fail-closed individual fields remain null/zero rather than fabricated numbers.

## Explicitly out of scope

- Multi-horizon method changes
- Default-on automatic calibration
- Actionable promotion, recommendations, orders
- Portfolio-level dashboards

## Related documents

- [0017-phase-16-calibration-readiness.md](0017-phase-16-calibration-readiness.md)
- [0020-phase-19-calibration-history.md](0020-phase-19-calibration-history.md)
- [0021-phase-20-outcome-label-history.md](0021-phase-20-outcome-label-history.md)
- [../overview.md](../overview.md)
