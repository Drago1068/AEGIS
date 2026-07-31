# ADR-0234: Phase 233 Evidence Summary Latest Assessment Label Block Reason (draft)

- Status: Proposed (ready after Phase 232; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 231–232 closed ``latest_assessment_is_label_ready``. Live AAPL evidence shows
``False`` with unlabeled latest and lag=119. Operators now know the latest row *cannot* be
labeled today, but not *which fail-closed gate* blocked it (``no_as_of_bar`` vs
``insufficient_forward_bars`` vs already labeled / other).

Domain already has ``OutcomeLabelReason`` and compute paths that raise those codes. Surfacing
a compact reason string is the natural evidence follow-on to the boolean — still not a nested
provenance scalar lift or UI modularization.

## Decisions (proposed)

### 1. API

Add ``latest_assessment_label_block_reason: str | null`` to
``ResearchEvidenceSummaryResponse`` (+ export):

- Null when no latest assessment, or when ``latest_assessment_is_label_ready`` is true.
- When not ready, set to a stable reason code aligned with ``OutcomeLabelReason`` (or a
  documented ``already_labeled`` if latest already has a label and readiness is moot —
  lock semantics in implementation).
- Never invent; derive from the same stored bars / gates as label compute.

### 2. Console

Surface near label-ready
(``data-testid="evidence-latest-assessment-label-block-reason"``).

### 3. Explicitly out of scope

- Nested UI extracts / redundant scalar lifts
- Default-on calibration, actionable promotion, orders, new scoring math

### 4. Why this next

Boolean answered "can we label?" Reason answers "why not?" — the remaining operator gap from
live AAPL evidence without inventing probabilities.

## Resume (after Phase 232 gate)

```powershell
# Implement latest_assessment_label_block_reason (ADR-0234); tests; commit+push; then Phase 234:
# git archive HEAD → NAS; rebuild backend+frontend TLS; then:
.\docker\nas\scripts\verify.ps1
# Expect: OK Phase 234 latest_assessment_label_block_reason=insufficient_forward_bars (or documented code)
```

## Related documents

- [0232-phase-231-evidence-summary-latest-assessment-is-label-ready.md](0232-phase-231-evidence-summary-latest-assessment-is-label-ready.md)
- [0233-phase-232-nas-live-verify-phase-231.md](0233-phase-232-nas-live-verify-phase-231.md)
- [0235-phase-234-nas-live-verify-phase-233.md](0235-phase-234-nas-live-verify-phase-233.md)
