# ADR-0071: Phase 70 NAS Live Verification of Phases 67–69

- Status: Accepted
- Date: 2026-07-30

## Context

Phases 67–69 added evidence-summary mixed label coverage fields
(``mixed_unlabeled_assessment_count``, ``latest_mixed_label_bar_source``,
``mixed_labeled_assessment_count``) and console display. Phase 68 prepared the first ops
gate for Phase 67, but live deploy/verify was blocked when NAS SSH port 22 refused
connections while the host still answered ICMP/HTTPS. Phase 70 is the **combined** ops
evidence gate for Phases 67–69 once SSH is restored.

## Decisions

### 1. Scope

Phase 70 is an **ops evidence gate** on the HTTPS lab profile:

1. Deploy current revision (``fcb554b`` or later) with the TLS overlay (native
   `linux/arm64` acceptable). Recreate backend and frontend.
2. Run `verify.ps1` / `verify.sh` successfully (prior ADR checks remain mandatory).
3. Authenticated ``GET .../evidence-summary`` (and export) must include:
   - ``mixed_unlabeled_assessment_count`` (integer ≥ 0)
   - ``mixed_labeled_assessment_count`` (integer ≥ 0)
   - ``latest_mixed_label_bar_source`` (string or null)
4. Invariant:  
   ``mixed_labeled + mixed_unlabeled == mixed_component_source_assessment_count``
5. When mixed count > 0 and labeled count > 0, ``latest_mixed_label_bar_source`` must be
   non-null.
6. SSH `alembic current` includes **`0009`** or `head`.

### 2. Relationship to Phase 68

Phase 68 checklist items remain in verify scripts. Successful Phase 70 live evidence
**satisfies** Phase 68 acceptance for Phase 67 fields as well. Do not mark either ops
phase live-verified without retained verify stdout after a successful redeploy.

### 3. Upload ≠ verified

Native build or `compose up` alone is not acceptance. Retain live verify stdout as evidence.

### 4. Out of scope

- New assessment/label math
- Default-on calibration
- ACME / public DNS
- Actionable promotion, recommendations, orders

## Resume when SSH recovers

```powershell
# From G:\Development\AEGIS with .env.nas loaded
# 1. Confirm: ssh -i $env:USERPROFILE\.ssh\ugreen_deploy_ed25519 Drago1068@192.168.1.12 "echo ok"
# 2. git archive HEAD → stream to NAS → unpack under /home/Drago1068/aegis/src/aegis-src
# 3. docker compose ...tls... build backend frontend; force-recreate
# 4. .\docker\nas\scripts\verify.ps1
```

## Related documents

- [0068-phase-67-mixed-label-coverage-evidence-summary.md](0068-phase-67-mixed-label-coverage-evidence-summary.md)
- [0069-phase-68-nas-live-verify-phase-67.md](0069-phase-68-nas-live-verify-phase-67.md)
- [0070-phase-69-mixed-labeled-count-evidence-summary.md](0070-phase-69-mixed-labeled-count-evidence-summary.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
