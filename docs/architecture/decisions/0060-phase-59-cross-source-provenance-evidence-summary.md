# ADR-0060: Phase 59 Cross-Source Provenance in Evidence Summary

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 55–57 enable cross-source component fill and source-aware labeling so deep secondary
history can grow research corpora. Operators need an audit-friendly view of when the latest
assessment used ``component_source=mixed`` and which observation source labels resolve to,
without digging only into nested assessment/label payloads.

## Decisions

### 1. Evidence-summary provenance fields

``GET /research/{symbol}/evidence-summary`` (and export) add:

- ``latest_component_source`` — from latest assessment ``components.component_source`` (else
  ``input_source``); null when no assessment
- ``latest_resolved_label_bar_source`` — persisted ``label.bar_source`` when a latest label
  exists; otherwise ``resolve_label_bar_source(assessment)``; null when no assessment
- ``mixed_component_source_assessment_count`` — count among the newest ≤100 assessments with
  component source ``mixed``

Missing pieces remain null or zero. No invented confidence or labels.

### 2. Console

Research console evidence-summary section surfaces the three fields and annotates
``mixed`` as cross-source fill (research only). Assessment component source display notes
``mixed`` the same way.

### 3. Out of scope

- Changing assessment/label math or fail-closed gates
- Default-on calibration
- Actionable promotion, orders, ACME
- NAS live verify (follow-up ops phase)

## Related documents

- [0023-phase-22-research-evidence-summary.md](0023-phase-22-research-evidence-summary.md)
- [0012-phase-11-multi-source-coverage-weighting.md](0012-phase-11-multi-source-coverage-weighting.md)
- [0056-phase-55-research-cross-source-session-depth.md](0056-phase-55-research-cross-source-session-depth.md)
- [0058-phase-57-source-aware-label-backfill-throughput.md](0058-phase-57-source-aware-label-backfill-throughput.md)
