# ADR-0270: Phase 269 Advance Store Tip When Provider Has Current Session (draft)

- Status: Proposed (ready after Phase 268; do not start until gate approved)
- Date: 2026-07-31

## Context

Phases 267–268 closed opaque mixed ``latest_resolved_label_bar_source`` (now concrete
``polygon`` on live AAPL). Live verify still shows ``stored_bar_calendar_lag_trading_days=1``
with winning tip ``2026-07-30`` after the ``2026-07-31`` session (post-close lab time).
Primary tip remains ``2026-07-29``. Operators cannot tell whether lag is expected
provider delay, AV failover, or a store/assessment short-circuit without another inspect.

Prefer diagnosing and closing the remaining calendar lag (when providers already expose
the current session close) over further evidence-summary scalars or UI modularization.

## Decisions (proposed)

### 1. Fail-closed tip advancement

Investigate why ingest/store tip stays one session behind after market close when a
configured provider has the session. Fix only with real provider closes; never invent
bars. Keep research-only / no orders.

### 2. Out of scope

Inventing closes, default-on calibration, actionable promotion, orders.

### 3. Why this next

Label-bar provenance is clear; remaining operator gap is calendar lag=1 after session
close.

## Resume (after Phase 268 gate)

```powershell
# Diagnose/fix store tip lag when provider has current session (ADR-0270); tests; commit+push; then Phase 270:
# git archive HEAD → NAS; rebuild backend TLS; then:
.\docker\nas\scripts\verify.ps1
```

## Related documents

- [0269-phase-268-nas-live-verify-phase-267.md](0269-phase-268-nas-live-verify-phase-267.md)
- [0271-phase-270-nas-live-verify-phase-269.md](0271-phase-270-nas-live-verify-phase-269.md)
- [0262-phase-261-provider-tip-ahead-of-store.md](0262-phase-261-provider-tip-ahead-of-store.md)
