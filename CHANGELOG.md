# Changelog

All notable changes to this project are documented in this file. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses phase-based
versioning until a first stable release (see [CLAUDE.md](CLAUDE.md) for the phase-gated
delivery workflow).

## [Unreleased]

### Phase 56 - NAS Live Verification of Phase 55

Ops evidence gate: redeploy under lab TLS with cross-source fill enabled and session-depth
research loads live. See
[docs/architecture/decisions/0057-phase-56-nas-live-verify-phase-55.md](docs/architecture/decisions/0057-phase-56-nas-live-verify-phase-55.md).

#### Added

- ADR-0057: live verify requires ``AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=true``
  on ``.env.nas``, backend recreate, and prefer new assessment backfill persists when older
  secondary-filled as-of dates unlock.
- Verify checklist item for the cross-source fill flag.

#### Explicitly out of scope

New assessment math, default-on calibration, ACME, actionable promotion, orders.

### Phase 55 - Research Cross-Source Fill and Session-Depth Bar Load

Unlock older assessment as-of dates when primary compact history is shallow but secondary
(Polygon) history is deep. See
[docs/architecture/decisions/0056-phase-55-research-cross-source-session-depth.md](docs/architecture/decisions/0056-phase-55-research-cross-source-session-depth.md).

#### Changed

- Default ``AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL`` to ``true`` (still overridable).
- Research bar loads use ``list_recent_for_sessions`` so ``AEGIS_RESEARCH_BAR_LOAD_LIMIT``
  counts distinct trading dates, not dual-source observation rows.
- Compose pass-through for the cross-source fill flag (local + NAS).

#### Explicitly out of scope

NAS live verify, default-on calibration, actionable promotion, orders, ACME.

### Phase 54 - NAS Live Verification of Phase 53

Ops evidence gate: redeploy under lab TLS with ``AEGIS_DAILY_BAR_OUTPUT_SIZE=full``,
re-ingest, and verify deeper stored bars unlock backfill growth. See
[docs/architecture/decisions/0055-phase-54-nas-live-verify-phase-53.md](docs/architecture/decisions/0055-phase-54-nas-live-verify-phase-53.md).

#### Added

- ADR-0055: live verify requires ``full`` output size on ``.env.nas``, backend recreate,
  authenticated ingest, and retained Phase 48/50 coupling.
- Compose pass-through for daily-bar primary/secondary sources and Polygon API key so
  Alpha Vantage premium ``full`` gates can failover to Polygon.
- Verify checklist item for ``AEGIS_DAILY_BAR_OUTPUT_SIZE=full``.

#### Explicitly out of scope

New assessment math, default-on calibration, ACME, actionable promotion, orders.

### Phase 53 - Full Daily-Bar History for Research Corpus Growth

Default provider lookback to ``full`` so ``AEGIS_RESEARCH_BAR_LOAD_LIMIT=252`` can load
deeper stored series after re-ingest. See
[docs/architecture/decisions/0054-phase-53-full-daily-bar-history.md](docs/architecture/decisions/0054-phase-53-full-daily-bar-history.md).

#### Changed

- ``AEGIS_DAILY_BAR_OUTPUT_SIZE`` default ``full`` (``compact`` remains valid for light labs).
- Compose backend pass-through for ``AEGIS_DAILY_BAR_OUTPUT_SIZE`` (local + NAS overlay).
- Ops note: recreate backend and re-run ingest after switching an existing deploy to ``full``.
- Document that free Alpha Vantage rejects ``outputsize=full`` (premium); secondary Polygon
  failover is the research path when configured.

#### Explicitly out of scope

Automatic history rebuild jobs, guaranteeing readiness ``ready``, default-on calibration,
actionable promotion, orders, ACME.

### Phase 52 - NAS Live Verification of Phase 51

Ops evidence gate: redeploy under the lab TLS profile with
``AEGIS_RESEARCH_BAR_LOAD_LIMIT=252`` and verify assessment/label backfill on the live NAS.
See
[docs/architecture/decisions/0053-phase-52-nas-live-verify-phase-51.md](docs/architecture/decisions/0053-phase-52-nas-live-verify-phase-51.md).

#### Added

- ``AEGIS_RESEARCH_BAR_LOAD_LIMIT`` wired into Compose backend environment (local + NAS
  overlay) so ``.env.nas`` / ``.env`` values reach the container (default ``252``).
- ADR-0053: live verify requires bar-load setting on ``.env.nas`` and retains Phase 48/50
  coupling; new assessment persistence preferred when deeper stored bars unlock candidates.
- Checklist / docs updates for Phase 52.

#### Explicitly out of scope

Ingest ``outputsize`` / re-ingest, new assessment math, default-on calibration, ACME,
actionable promotion, orders.

### Phase 51 - Configurable Research Bar Load Limit

Configurable recent-bar depth for assessment and outcome-label paths so operators can grow
beyond a saturated 120-bar window. See
[docs/architecture/decisions/0052-phase-51-research-bar-load-limit.md](docs/architecture/decisions/0052-phase-51-research-bar-load-limit.md).

#### Added

- ``AEGIS_RESEARCH_BAR_LOAD_LIMIT`` (default ``252``) shared by on-demand assess, assessment
  backfill, and outcome-label / Phase 49 selection (ADR-0052).
- Assessment backfill existing as-of scan expands with the configured bar load.

#### Explicitly out of scope

Guaranteeing readiness ``ready``, ingest depth changes, auto-chaining backfills, default-on
calibration, actionable promotion, orders, ACME.

### Phase 50 - NAS Live Verification of Phase 49

Ops evidence gate: redeploy under the lab TLS profile and verify unlabeled label-ready
outcome-label backfill (``limit=20``) on the live NAS. See
[docs/architecture/decisions/0051-phase-50-nas-live-verify-phase-49.md](docs/architecture/decisions/0051-phase-50-nas-live-verify-phase-49.md).

#### Added

- ADR-0051: live verify confirms Phase 48 coupling still holds with outcome-label backfill
  ``limit=20`` after Phase 49 candidate selection.
- Checklist / docs updates for Phase 50.

#### Explicitly out of scope

New assessment/label math, default-on calibration, ACME, actionable promotion, orders.

### Phase 49 - Prefer Unlabeled Label-Ready Outcome-Label Backfill

Prefer unlabeled assessments with stored forward-horizon closes so default ``limit=20``
grows the labeled corpus without tip / already-labeled waste. See
[docs/architecture/decisions/0050-phase-49-prefer-unlabeled-label-backfill.md](docs/architecture/decisions/0050-phase-49-prefer-unlabeled-label-backfill.md).

#### Changed

- ``POST .../outcome-labels/backfill`` scans up to 100 assessments, omits rows that already
  have ``forward_total_return_v1`` labels or lack forward-horizon closes, then labels up to
  ``limit`` remaining candidates (ADR-0050).
- NAS verify outcome-label backfill uses ``limit=20`` again (Phase 48 coupling retained).

#### Explicitly out of scope

Raising ``BAR_LOAD_LIMIT``, auto-chaining assessment→label backfill, default-on calibration,
actionable promotion, orders, ACME.

### Phase 48 - NAS Live Verification of Phase 47

Ops evidence gate: redeploy under the lab TLS profile and verify label-ready assessment
backfill coupling on the live NAS. See
[docs/architecture/decisions/0049-phase-48-nas-live-verify-phase-47.md](docs/architecture/decisions/0049-phase-48-nas-live-verify-phase-47.md).

#### Added

- ADR-0049: live verify retains Phase 46 assessment-backfill checks and adds Phase 48
  coupling (when assessments ``persisted_count > 0``, outcome-label backfill must
  ``persisted_count >= 1``; label backfill uses ``limit=100``).
- `verify.ps1` / `verify.sh` Phase 48 gates.

#### Explicitly out of scope

New assessment/label math, default-on calibration, ACME, actionable promotion, orders.

### Phase 47 - Label-Ready Assessment Backfill Candidates

Prefer as-of dates that already have stored forward-horizon closes so Phase 43 labeling
can persist. See
[docs/architecture/decisions/0048-phase-47-label-ready-assessment-backfill.md](docs/architecture/decisions/0048-phase-47-label-ready-assessment-backfill.md).

#### Changed

- Assessment backfill candidate selection (ADR-0048): newest-first among primary dates
  with a close on the session ``max(FORWARD_HORIZON_SESSIONS)`` after ``as_of``; tip dates
  without forward coverage are omitted (``candidate_count=0`` when none qualify).

#### Explicitly out of scope

Default-on calibration, auto-label after assessment backfill, raising bar load limits,
actionable promotion, orders, ACME.

### Phase 46 - NAS Live Verification of Phase 45

Ops evidence gate: redeploy current revision under the lab TLS profile and verify
assessment backfill on the live NAS. See
[docs/architecture/decisions/0047-phase-46-nas-live-verify-phase-45.md](docs/architecture/decisions/0047-phase-46-nas-live-verify-phase-45.md).

#### Added

- ADR-0047: live verify includes unauth **401** and auth **200** summary for
  `POST .../assessments/backfill`.
- `verify.ps1` / `verify.sh` Phase 46 gates.

#### Explicitly out of scope

New assessment math, default-on calibration, ACME, actionable promotion, orders.

### Phase 45 - Historical Research Assessment Backfill

Research-only batch creation of point-in-time assessments for past primary bar dates so
operators can grow labeled corpus candidates. See
[docs/architecture/decisions/0046-phase-45-assessment-backfill.md](docs/architecture/decisions/0046-phase-45-assessment-backfill.md).

#### Added

- `POST /research/{symbol}/assessments/backfill?limit=` — truncate bars to each as-of,
  fail-closed per date, always 200 with summary counts.
- Operator console "Backfill assessments" control.
- ADR-0046.

#### Explicitly out of scope

Default-on calibration, auto-labeling during assessment backfill, rewriting history,
actionable promotion, orders, ACME/public TLS.

### Phase 44 - NAS Live Verification of Phase 43

Ops evidence gate: redeploy current revision under the lab TLS profile and verify
outcome-label backfill on the live NAS. See
[docs/architecture/decisions/0045-phase-44-nas-live-verify-phase-43.md](docs/architecture/decisions/0045-phase-44-nas-live-verify-phase-43.md).

#### Added

- ADR-0045: live verify includes unauth **401** and auth **200** summary for
  `POST .../outcome-labels/backfill`.
- `verify.ps1` / `verify.sh` Phase 44 gates.

#### Explicitly out of scope

New labeling math, default-on calibration, ACME, actionable promotion, orders.

### Phase 43 - Historical Outcome-Label Backfill

Research-only batch re-attempt of `forward_total_return_v1` labels over recent assessment
history so operators can grow the labeled corpus toward calibration readiness. See
[docs/architecture/decisions/0044-phase-43-outcome-label-backfill.md](docs/architecture/decisions/0044-phase-43-outcome-label-backfill.md).

#### Added

- `POST /research/{symbol}/outcome-labels/backfill?limit=` — fail-closed per assessment;
  always 200 with summary counts.
- Operator console "Backfill outcome labels" control.
- ADR-0044.

#### Explicitly out of scope

Default-on calibration, new horizons, guaranteeing readiness `ready`, actionable promotion,
orders, ACME/public TLS.

### Phase 42 - NAS Live Verification of Phase 41

Ops evidence gate: redeploy current revision under the lab TLS profile and verify
multi-horizon calibration readiness (`by_horizon`, alembic `0009`) on the live NAS. See
[docs/architecture/decisions/0043-phase-42-nas-live-verify-phase-41.md](docs/architecture/decisions/0043-phase-42-nas-live-verify-phase-41.md).

#### Added

- ADR-0043: live verify asserts readiness/`export` `by_horizon` for `forward_return_5` and
  `forward_return_20`; optional authenticated `POST .../calibrations?horizon=` (200 or
  fail-closed 422).
- `verify.ps1` / `verify.sh` Phase 42 gates (alembic `0009` already required).

#### Explicitly out of scope

ACME, new horizons, default-on calibration, actionable promotion, orders.

### Phase 41 - Multi-Horizon Probability Calibration

Horizon-specific research_calibration_v1 for `forward_return_5` and `forward_return_20`. See
[docs/architecture/decisions/0042-phase-41-multi-horizon-calibration.md](docs/architecture/decisions/0042-phase-41-multi-horizon-calibration.md).

#### Added

- Alembic `0009` `outcome_horizon_key` on calibration rows (backfill `forward_return_5`).
- `POST .../calibrations?horizon=`; readiness `by_horizon[]`; console horizon surfacing.
- ADR-0042.

#### Explicitly out of scope

New horizons beyond 5/20, default-on calibration, actionable promotion, orders, TLS changes.

### Phase 40 - NAS Lab TLS Live Cutover

Enable Phase 9 Caddy TLS on the live NAS with lab hosts, remapped ports, and self-signed
PEMs. See
[docs/architecture/decisions/0041-phase-40-nas-lab-tls-cutover.md](docs/architecture/decisions/0041-phase-40-nas-lab-tls-cutover.md)
and [docs/operations/nas-tls-cutover.md](docs/operations/nas-tls-cutover.md).

#### Added

- ADR-0041 lab profile (`aegis.local` / `api.aegis.local`, HTTPS `18443`, HTTP `18080`).
- Cutover/rollback runbook; `generate-lab-certs.ps1` / `.sh`.
- Caddy non-443 redirect via `AEGIS_TLS_HTTPS_PORT`; verify Caddy running + optional
  `AEGIS_NAS_VERIFY_CURL_RESOLVE`.

#### Explicitly out of scope

ACME, public DNS, multi-horizon calibration, default-on calibration, actionable promotion,
orders.

### Phase 39 - NAS Live Verification of Phase 38

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/assessments/export` on the live NAS. See
[docs/architecture/decisions/0040-phase-39-nas-live-verify-phase-38.md](docs/architecture/decisions/0040-phase-39-nas-live-verify-phase-38.md).

#### Added

- ADR-0040: live verify includes assessments export (401 unauth; attachment array when auth).
- `verify.ps1` / `verify.sh` assessments export auth gate + authenticated attachment check.

#### Explicitly out of scope

New assessment methods, default-on calibration, actionable promotion, orders, TLS cutover.

### Phase 38 - Assessment History JSON Export

Authenticated download of append-only research assessments for a symbol. See
[docs/architecture/decisions/0039-phase-38-assessments-export.md](docs/architecture/decisions/0039-phase-38-assessments-export.md).

#### Added

- `GET /research/{symbol}/assessments/export?limit=` — same JSON array as the list route
  with `Content-Disposition: attachment`.
- Operator console "Download assessments JSON" control.
- ADR-0039.

#### Explicitly out of scope

Default-on calibration, new methods, actionable promotion, orders, TLS cutover, CSV/PDF.

### Phase 37 - NAS Live Verification of Phase 36

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/assessments/{id}/calibrations/export` on the live NAS. See
[docs/architecture/decisions/0038-phase-37-nas-live-verify-phase-36.md](docs/architecture/decisions/0038-phase-37-nas-live-verify-phase-36.md).

#### Added

- ADR-0038: live verify includes calibrations export (401 unauth; attachment array when auth).
- `verify.ps1` / `verify.sh` calibrations export auth gate + authenticated attachment check.

#### Explicitly out of scope

New calibration methods, default-on calibration, actionable promotion, orders, TLS cutover.

### Phase 36 - Calibration History JSON Export

Authenticated download of append-only probability calibrations for an assessment. See
[docs/architecture/decisions/0037-phase-36-calibrations-export.md](docs/architecture/decisions/0037-phase-36-calibrations-export.md).

#### Added

- `GET /research/{symbol}/assessments/{id}/calibrations/export?limit=` — same JSON array
  as the list route with `Content-Disposition: attachment`.
- Operator console "Download calibrations JSON" control.
- ADR-0037.

#### Explicitly out of scope

Default-on calibration, new methods, actionable promotion, orders, TLS cutover, CSV/PDF.

### Phase 35 - NAS Live Verification of Phase 34

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/assessments/{id}/outcome-labels/export` on the live NAS. See
[docs/architecture/decisions/0036-phase-35-nas-live-verify-phase-34.md](docs/architecture/decisions/0036-phase-35-nas-live-verify-phase-34.md).

#### Added

- ADR-0036: live verify includes outcome-labels export (401 unauth; attachment array when auth).
- `verify.ps1` / `verify.sh` outcome-labels export auth gate + authenticated attachment check.

#### Explicitly out of scope

New label methods, default-on calibration, actionable promotion, orders, TLS cutover.

### Phase 34 - Outcome-Label History JSON Export

Authenticated download of append-only outcome labels for an assessment. See
[docs/architecture/decisions/0035-phase-34-outcome-labels-export.md](docs/architecture/decisions/0035-phase-34-outcome-labels-export.md).

#### Added

- `GET /research/{symbol}/assessments/{id}/outcome-labels/export?limit=` — same JSON array
  as the list route with `Content-Disposition: attachment`.
- Operator console "Download outcome labels JSON" control.
- ADR-0035.

#### Explicitly out of scope

New label methods, default-on calibration, actionable promotion, orders, TLS cutover,
CSV/PDF.

### Phase 33 - NAS Live Verification of Phase 32

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/calibration-readiness/export` on the live NAS. See
[docs/architecture/decisions/0034-phase-33-nas-live-verify-phase-32.md](docs/architecture/decisions/0034-phase-33-nas-live-verify-phase-32.md).

#### Added

- ADR-0034: live verify includes readiness export (401 unauth; attachment when auth).
- `verify.ps1` / `verify.sh` readiness export auth gate + authenticated attachment check.

#### Explicitly out of scope

Default-on calibration, horizon-specific methods, actionable promotion, orders, TLS cutover.

### Phase 32 - Calibration Readiness JSON Export

Authenticated download of calibration readiness diagnostics for offline audit. See
[docs/architecture/decisions/0033-phase-32-calibration-readiness-export.md](docs/architecture/decisions/0033-phase-32-calibration-readiness-export.md).

#### Added

- `GET /research/{symbol}/calibration-readiness/export` — same payload as readiness with
  `Content-Disposition: attachment`.
- Operator console "Download readiness JSON" control.
- ADR-0033.

#### Explicitly out of scope

Default-on calibration, horizon-specific methods, actionable promotion, orders, TLS cutover,
CSV/PDF.

### Phase 31 - NAS Live Verification of Phase 30

Ops evidence gate: redeploy current revision (Phase 30 end-date UI) and re-run live verify
on the NAS. See
[docs/architecture/decisions/0032-phase-31-nas-live-verify-phase-30.md](docs/architecture/decisions/0032-phase-31-nas-live-verify-phase-30.md).

#### Added

- ADR-0032: redeploy + verify; evidence-summary logs present `label_end_dates` keys only.
- `verify.ps1` / `verify.sh` log `end_date_keys` alongside label keys.

#### Explicitly out of scope

New methods, horizon-specific calibration, default-on calibration, actionable promotion,
orders, TLS cutover.

### Phase 30 - Outcome Label End-Date Surfacing

Operator console shows `label_end_dates` next to present horizon returns (API payload only).
See
[docs/architecture/decisions/0031-phase-30-label-end-date-surfacing.md](docs/architecture/decisions/0031-phase-30-label-end-date-surfacing.md).

#### Changed

- Outcome-label detail, history, and evidence summary include end trading dates when present.
- ADR-0031.

#### Explicitly out of scope

New horizons/methods, horizon-specific calibration, default-on calibration, actionable
promotion, orders, TLS cutover.

### Phase 29 - NAS Live Verification of Phase 28

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/assessments?limit=` on the live NAS. See
[docs/architecture/decisions/0030-phase-29-nas-live-verify-phase-28.md](docs/architecture/decisions/0030-phase-29-nas-live-verify-phase-28.md).

#### Added

- ADR-0030: live verify includes assessments list (401 unauth; 200 JSON array when auth).
- `verify.ps1` / `verify.sh` assessments list auth gate + authenticated check.

#### Explicitly out of scope

New methods, horizon-specific calibration, default-on calibration, actionable promotion,
orders, TLS cutover.

### Phase 28 - Research Assessment History in the Console

Operator console shows newest-first assessment history from the existing list API. See
[docs/architecture/decisions/0029-phase-28-assessment-history-console.md](docs/architecture/decisions/0029-phase-28-assessment-history-console.md).

#### Added

- Assessment history block (when more than one snapshot): computed_at, research_index,
  coverage_confidence, probability_confidence (null-safe).
- ADR-0029.

#### Explicitly out of scope

New assessment methods, horizon-specific calibration, default-on calibration, actionable
promotion, orders, TLS cutover.

### Phase 27 - NAS Live Verification of Phase 26

Ops evidence gate: redeploy current revision (Phase 26 multi-horizon UI) and re-run live
verify on the NAS. See
[docs/architecture/decisions/0028-phase-27-nas-live-verify-phase-26.md](docs/architecture/decisions/0028-phase-27-nas-live-verify-phase-26.md).

#### Added

- ADR-0028: redeploy + verify; evidence-summary logs present label keys only.
- `verify.ps1` / `verify.sh` log present `forward_return_*` keys when labels exist.

#### Explicitly out of scope

New horizons/methods, horizon-specific calibration, default-on calibration, actionable
promotion, orders, TLS cutover.

### Phase 26 - Multi-Horizon Outcome Label Surfacing

Operator console shows every horizon key present on outcome-label payloads (5 and 20
session returns already computed by Phase 13). See
[docs/architecture/decisions/0027-phase-26-multi-horizon-label-surfacing.md](docs/architecture/decisions/0027-phase-26-multi-horizon-label-surfacing.md).

#### Changed

- Evidence summary and outcome-label history render all API `labels` keys (sorted); no
  invented values.
- ADR-0027.

#### Explicitly out of scope

New horizons/methods, horizon-specific calibration, default-on calibration, actionable
promotion, orders, TLS cutover.

### Phase 25 - NAS Live Verification of Phase 24

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/evidence-summary/export` on the live NAS. See
[docs/architecture/decisions/0026-phase-25-nas-live-verify-phase-24.md](docs/architecture/decisions/0026-phase-25-nas-live-verify-phase-24.md).

#### Added

- ADR-0026: live verify includes evidence-summary export (401 unauth; attachment +
  `research_only` when authenticated).
- `verify.ps1` / `verify.sh` export auth gate + authenticated attachment check.

#### Explicitly out of scope

Default-on calibration, multi-horizon methods, actionable promotion, orders, TLS cutover.

### Phase 24 - Research Evidence Summary JSON Export

Authenticated download of the research-only evidence aggregate for offline audit. See
[docs/architecture/decisions/0025-phase-24-evidence-summary-export.md](docs/architecture/decisions/0025-phase-24-evidence-summary-export.md).

#### Added

- `GET /research/{symbol}/evidence-summary/export` — same payload as evidence-summary with
  `Content-Disposition: attachment`.
- Operator console "Download evidence JSON" control.
- ADR-0025.

#### Explicitly out of scope

Multi-horizon methods, default-on calibration, actionable promotion, orders, CSV/PDF.

### Phase 23 - NAS Live Verification of Phase 22

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/evidence-summary` on the live NAS. See
[docs/architecture/decisions/0024-phase-23-nas-live-verify-phase-22.md](docs/architecture/decisions/0024-phase-23-nas-live-verify-phase-22.md).

#### Added

- ADR-0024: live verify includes authenticated evidence-summary (state=`research_only`).
- `verify.ps1` / `verify.sh` evidence-summary auth gate + authenticated check.

#### Explicitly out of scope

Default-on calibration, multi-horizon methods, actionable promotion, orders.

### Phase 22 - Symbol Research Evidence Summary

Authenticated read-only aggregate of research evidence for one symbol (latest assessment,
readiness, latest label/calibration, history counts). See
[docs/architecture/decisions/0023-phase-22-research-evidence-summary.md](docs/architecture/decisions/0023-phase-22-research-evidence-summary.md).

#### Added

- ADR-0023: `GET /research/{symbol}/evidence-summary`; operator console evidence summary
  section. Missing fields are null/zero — never invented.

#### Explicitly out of scope

Multi-horizon methods, default-on calibration, actionable promotion, orders.

### Phase 21 - NAS Live Verification of Phases 18–20

Ops evidence gate: redeploy current revision to the UGREEN NAS and verify on-demand
calibration plus calibration/outcome-label history routes. See
[docs/architecture/decisions/0022-phase-21-nas-live-verify-phases-18-20.md](docs/architecture/decisions/0022-phase-21-nas-live-verify-phases-18-20.md).

#### Added

- ADR-0022: live verify includes authenticated `GET .../calibrations` and
  `GET .../outcome-labels` (JSON arrays; empty `[]` allowed).
- `verify.ps1` history list checks after login.

#### Explicitly out of scope

Default-on calibration, multi-horizon methods, actionable promotion, orders.

### Phase 20 - Outcome Label History

Authenticated list of append-only `forward_total_return_v1` rows for an assessment so
operators can audit repeated labeling. See
[docs/architecture/decisions/0021-phase-20-outcome-label-history.md](docs/architecture/decisions/0021-phase-20-outcome-label-history.md).

#### Added

- ADR-0021: `GET .../assessments/{id}/outcome-labels?limit=` (newest first; empty `[]` when
  none); operator console label history when more than one row exists.
- Mirrors Phase 19 calibration history; no new label method.

#### Explicitly out of scope

Multi-horizon method changes, default-on calibration, actionable promotion, orders.

### Phase 19 - Calibration History

Authenticated list of append-only `research_calibration_v1` rows for an assessment so
operators can audit repeated on-demand calibrations. See
[docs/architecture/decisions/0020-phase-19-calibration-history.md](docs/architecture/decisions/0020-phase-19-calibration-history.md).

#### Added

- ADR-0020: `GET .../assessments/{id}/calibrations?limit=` (newest first; empty `[]` when
  none); operator console calibration history when more than one row exists.
- Reuses Phase 15/18 persistence; no new method or automatic-calibration default change.

#### Explicitly out of scope

Multi-horizon methods, default-on calibration, actionable promotion, orders.

### Phase 18 - On-Demand Probability Calibration

Authenticated on-demand `research_calibration_v1` when readiness is `ready`, without enabling
global automatic calibration. See
[docs/architecture/decisions/0019-phase-18-on-demand-calibration.md](docs/architecture/decisions/0019-phase-18-on-demand-calibration.md).

#### Added

- ADR-0019: `POST` / `GET .../calibrations` and `.../calibrations/latest`; operator console
  “Compute calibration” when readiness status is `ready`.
- Reuses Phase 15 math and corpus gates; fail-closed HTTP 422; flag default remains `false`.

#### Explicitly out of scope

Default-on calibration, multi-horizon methods, actionable promotion, orders, and NAS live
deploy changes.

### Phase 17 - NAS Live Verification (Ops Evidence Gate)

Hardens the package/deploy/**verify** boundary for the current research-only stack: auth
gates include calibration-readiness, authenticated readiness checks, Alembic through `0008`,
and an explicit dry-run that is not acceptance evidence. See
[docs/architecture/decisions/0018-phase-17-nas-live-verification.md](docs/architecture/decisions/0018-phase-17-nas-live-verification.md)
and [docs/operations/nas-live-verification.md](docs/operations/nas-live-verification.md).

#### Added

- ADR-0018: live-verified definition; dry-run vs evidence.
- `verify.ps1` / `verify.sh`: calibration-readiness 401 gate, operator login + authenticated
  research/readiness checks, Alembic `0008|head`, `-DryRun` / `--dry-run`.
- Operator checklist and runbook updates; optional `AEGIS_NAS_VERIFY_SYMBOL`.

#### Explicitly out of scope

Default-on calibration, actionable promotion, orders, and NAS hardware provisioning.

### Phase 16 - Calibration Corpus Readiness & Operator Diagnostics

Read-only readiness diagnostics for Phase 15 corpus gates so operators can inspect whether
`research_calibration_v1` would pass before enabling calibration. See
[docs/architecture/decisions/0017-phase-16-calibration-readiness.md](docs/architecture/decisions/0017-phase-16-calibration-readiness.md).

#### Added

- ADR-0017: `GET /research/{symbol}/calibration-readiness`; domain
  `evaluate_calibration_readiness`; operator console readiness section.
- No new persistence; never invents `probability_confidence`.

#### Explicitly out of scope

Enabling calibration by default, actionable promotion, orders, and NAS live deployment.

### Phase 15 - Research Probability Calibration v1

First research-only `research_calibration_v1` empirical probability from stored labeled
historical corpus. Fail-closed when corpus gates fail; `state` remains `research_only`. See
[docs/architecture/decisions/0016-phase-15-research-probability-calibration.md](docs/architecture/decisions/0016-phase-15-research-probability-calibration.md).

#### Added

- ADR-0016: append-only `research_assessment_probability_calibrations` (migration `0008`);
  `AEGIS_RESEARCH_CALIBRATION_AFTER_LABEL_ENABLED` (default `false`); API overlay of latest
  calibration onto `probability_confidence`; scheduled/on-demand wiring after assessments.
- Operator console labels non-null probability as calibrated research-only.

#### Explicitly out of scope

Actionable promotion, orders, portfolio analytics, and NAS live deployment.

### Phase 14 - Scheduled Outcome Labels After Research Assessments

Automatic Phase 13 `forward_total_return_v1` labeling after successful research assessments
from post-ingest research and on-demand assessment creation. Fail-closed skips log and persist
nothing; `probability_confidence` remains null. See
[docs/architecture/decisions/0015-phase-14-scheduled-outcome-labels.md](docs/architecture/decisions/0015-phase-14-scheduled-outcome-labels.md).

#### Added

- ADR-0015: `AEGIS_RESEARCH_OUTCOME_LABEL_AFTER_ASSESSMENT_ENABLED` (local and NAS example
  default `true`); domain orchestration `scheduled_outcome_labels`; wiring in scheduled ingest
  lock, on-demand ingest, and on-demand assessment paths.
- Post-ingest research summary now carries persisted `assessment_snapshot_id` for labeling.

#### Explicitly out of scope

Probability calibration, actionable promotion, orders, and new label methods.

### Phase 13 - Research Outcome Labels (Calibration Evidence Prep)

Append-only forward-return outcome labels linked to research assessment snapshots.
`probability_confidence` remains null; labels are evidence only, not calibrated
probabilities. See
[docs/architecture/decisions/0014-phase-13-research-outcome-labels.md](docs/architecture/decisions/0014-phase-13-research-outcome-labels.md).

#### Added

- ADR-0014: `forward_total_return_v1` horizons 5 and 20 trading sessions; fail-closed;
  on-demand POST/GET under `/research/{symbol}/assessments/{id}/outcome-labels`.
- Table `research_assessment_outcome_labels` (migration `0007`).
- Operator console presentation of outcome labels when available.

#### Explicitly out of scope

Probability calibration, actionable promotion, orders. Automatic post-assessment labeling is
added in Phase 14 (ADR-0015).

### Phase 12 - Provider Historical Corrections (Append-Only)

When a provider revises a historical daily bar, AEGIS inserts a new `correction` observation
row with provenance instead of silently skipping or overwriting the prior row. Reads return
the latest `ingested_at` per `(source, symbol, trading_date)`. See
[docs/architecture/decisions/0013-phase-12-provider-historical-corrections.md](docs/architecture/decisions/0013-phase-12-provider-historical-corrections.md).

#### Added

- ADR-0013: material change detection, `observation_kind`, `supersedes_observation_id`,
  current-bar read policy, out of scope.
- Alembic `0006`: drop unique constraint on `(source, symbol, event_time)`; add correction
  columns and index for current-bar queries.
- Domain `bars_materially_differ`; ingestion inserts corrections with structured logging;
  `corrected_count` on ingest results.
- Setting `AEGIS_MARKET_DATA_CORRECTION_PRICE_EPSILON` (default `1e-6`).

#### Explicitly out of scope

Calibration, blended bars, actionable promotion, orders, correction history API, and live NAS
deploy from this phase.

### Phase 11 - Multi-Source Coverage Weighting (Research-Only)

Extends research assessment `coverage_confidence` with multi-source availability and
agreement factors when multiple daily-bar sources exist for a symbol's lookback window.
Component return/vol/index series stay single preferred source (no OHLCV blend).
`probability_confidence` remains null; `state` remains `research_only`. See
[docs/architecture/decisions/0012-phase-11-multi-source-coverage-weighting.md](docs/architecture/decisions/0012-phase-11-multi-source-coverage-weighting.md).

#### Added

- ADR-0012: method_version 2, preferred-source components, coverage formula, disagreement
  floor (`0.80`), feature flag, provenance fields, out of scope.
- Domain: multi-source factors on `daily_bar_research_v1`; optional cross-source component
  fill (default off); optional disagreement fail-closed; schema_version 2 components
  provenance.
- Settings / `.env.example` / `.env.nas.example`:
  `AEGIS_RESEARCH_MULTI_SOURCE_COVERAGE_ENABLED`,
  `AEGIS_RESEARCH_MULTI_SOURCE_CLOSE_TOLERANCE`,
  `AEGIS_RESEARCH_MULTI_SOURCE_DISAGREEMENT_FAIL_CLOSED`,
  `AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL`.
- Operator console: presentation-only factor / component-source fields when present.
- Tests for single-source agreement=1, soft disagreement penalty, hard reject, and fill.

#### Explicitly out of scope

Calibration, blended bars, corrections, actionable promotion, orders, and live NAS deploy
from this phase.

### Phase 10 - Second Daily-Bar Market-Data Provider (Polygon + failover)

Adds Polygon.io daily aggregates as a second typed `DailyBarProvider`, with configuration-
driven primary selection and optional per-symbol failover on rate-limit / unavailable
errors. Alpha Vantage remains selectable as primary or secondary. Research method
unchanged (`research_only`, `probability_confidence=null`). See
[docs/architecture/decisions/0011-phase-10-second-market-data-provider.md](docs/architecture/decisions/0011-phase-10-second-market-data-provider.md).

#### Added

- ADR-0011: provider pick, source ids (`alpha_vantage`, `polygon`), failover matrix, out of
  scope.
- `aegis.providers.polygon.PolygonProvider` (unadjusted daily aggs; Bearer auth; typed
  errors); `ProviderUnavailableError`; settings for primary/secondary and Polygon keys.
- Shared ingest wiring for on-demand and scheduled paths; successful writes use the producing
  adapter's `source` (no silent provenance swap).
- Tests: Polygon httpx mocks; failover orchestration; settings validation. No live network
  in CI.
- Docs / `.env.example` / `.env.nas.example` placeholders.

#### Explicitly out of scope

Calibration, actionable promotion, orders, corrections, intraday, multi-source consensus /
blended bars, auth changes, and live NAS deploy from this phase.

### Phase 9 - NAS Reverse-Proxy / TLS Packaging for Secure Cookies

Optional Caddy reverse-proxy + TLS termination for the UGREEN NAS Compose stack so operators
can use HTTPS with `AEGIS_SESSION_COOKIE_SECURE=true`. Packaging and ops only; application
session auth (Phase 4) remains the source of truth. Proxy is TLS + routing — not Basic Auth.
No product scoring expansion. See
[docs/architecture/decisions/0010-phase-9-nas-tls-reverse-proxy.md](docs/architecture/decisions/0010-phase-9-nas-tls-reverse-proxy.md).

#### Added

- ADR-0010: prefer Caddy; optional Compose overlay; operator PEMs and/or ACME; dual-host
  routing; cookie/CORS fail-closed alignment; forwarded headers documented.
- `docker/nas/docker-compose.nas.tls.yml` (unpublish API/frontend host ports; publish 443/80;
  Caddy service).
- Proxy templates under `docker/nas/proxy/` (`Caddyfile.files`, `Caddyfile.acme`); certs
  directory placeholders only (no committed PEMs).
- `.env.nas.example` TLS placeholders; package/deploy/verify/validate-local honor
  `AEGIS_NAS_TLS_ENABLED` and fail closed without required TLS material.
- Docs: NAS runbook, nas-deployment, configuration, overview, CI compose dry-run for TLS.

#### Explicitly out of scope

Live NAS deploy from CI, OAuth/MFA, calibration, actionable promotion, orders, second
provider, and application auth changes - each remains absent. Local dev stays HTTP +
Secure=false.

### Phase 8 - Scheduled Research Assessments After Ingest

After each successful locked scheduled ingest cycle (and after successful on-demand
`POST /market-data/ingest` when configured), automatically run Phase 6
`daily_bar_research_v1` for active watchlist symbols using stored bars only. Persist
append-only snapshots on success; skip with structured logs on fail-closed (no row). Keep
`state=research_only`, coverage set, `probability_confidence=null`. See
[docs/architecture/decisions/0009-phase-8-scheduled-research.md](docs/architecture/decisions/0009-phase-8-scheduled-research.md).

#### Added

- Backend: `domain.scheduled_research.run_research_after_ingest` (Protocol-based, per-symbol
  fail-closed); optional research inside `run_locked_ingestion_cycle` before lock release;
  scheduler and on-demand ingest wiring; setting
  `AEGIS_RESEARCH_SCHEDULE_AFTER_INGEST_ENABLED` (local and NAS example default `true`).
- Frontend: research panel copy notes post-ingest snapshots may appear after ingest
  (presentation only; RESEARCH ONLY labels unchanged).
- Docs: ADR-0009; overview and configuration updates; `.env.example` / `.env.nas.example`.

#### Explicitly out of scope

Calibration, actionable promotion, recommendations, chart signals, orders, TLS changes, and
NAS live verify - each remains absent.

### Phase 7 - UGREEN NAS Deployment Packaging

Packages the existing research-only authenticated stack for UGREEN NAS DXP-series hardware
(`linux/amd64`). Does not add actionable promotion, calibration, scheduled assessments, a
second provider, orders, OAuth, MFA, or RBAC. See
[docs/architecture/decisions/0008-phase-7-nas-deployment.md](docs/architecture/decisions/0008-phase-7-nas-deployment.md)
and [docker/nas/README.md](docker/nas/README.md).

#### Added

- Compose overlay `docker/nas/docker-compose.nas.yml` (extends root compose; no fork): amd64
  platform, always-restart, Postgres/Redis unpublished on the host, production-leaning
  defaults, image tags for save/load.
- `.env.nas.example` placeholders; `.env.nas` gitignored; frontend Dockerfile build-arg for
  `NEXT_PUBLIC_API_BASE_URL` (baked at package time).
- Scripts under `docker/nas/scripts/`: `package`, `deploy`, `verify`, `validate-local`
  (PowerShell + shell). Fail closed on missing env; reject default/template NAS passwords.
  Deploy applies Alembic through `0005`; verify checks health/ready/auth gate/key routes/
  frontend and documents log inspection. Upload ≠ verified deployment.
- Docs: ADR-0008; NAS runbook; `docs/operations/nas-deployment.md`; overview/README/CI notes.

#### Explicitly out of scope

Actionable promotion, calibration, scheduled assessments, second provider, order placement,
OAuth/MFA/RBAC, and committed hostnames/IPs/credentials - each remains absent.

### Phase 6 - Research-Only Scoring Foundations

On-demand research-only assessments over stored primary daily bars. Fail-closed when inputs
are incomplete; every success payload is `state=research_only` with non-null
`coverage_confidence` and null `probability_confidence`. No recommendations, actionable
promotion, calibration, or order placement; see
[docs/architecture/decisions/0007-phase-6-research-only-scoring.md](docs/architecture/decisions/0007-phase-6-research-only-scoring.md).

#### Added

- Backend: domain method `daily_bar_research_v1` (20-session return, annualized realized vol,
  `research_index`); append-only `research_assessment_snapshots` (Alembic `0005`);
  authenticated `POST/GET /research/{symbol}/assessments` and
  `GET /research/{symbol}/assessments/latest`; HTTP 422 structured `detail.reason` on gate
  failures with no persistence.
- Frontend: `ResearchAssessmentPanel` on `/symbols/[symbol]` with RESEARCH ONLY labeling;
  typed API client methods; presentation-only (no client-side research math).
- Docs: ADR-0007; architecture overview and data-model updates for research snapshots.

#### Explicitly out of scope

Actionable promotion, calibration / non-null probability confidence, scheduled assessments,
chart signal overlays, second provider, OAuth/MFA, order placement, and NAS deployment -
each is absent, not merely unimplemented, per the Phase 6 plan.

### Phase 5 - Daily Bar Charts

Candlestick OHLC + volume charts on the authenticated symbol page, using the existing
daily-bars API and TradingView Lightweight Charts. No scoring, recommendation, prediction,
indicators, signals, or order-placement logic exists in this phase; see
[docs/architecture/decisions/0006-phase-5-daily-bar-charts.md](docs/architecture/decisions/0006-phase-5-daily-bar-charts.md).

#### Added

- Frontend: `lightweight-charts` dependency; `DailyBarsChart` Client Component (candlestick +
  volume histogram, dispose on unmount, empty/error-safe); adapter mapping newest-first API
  bars to chronological series; chart above `DailyBarsTable` on `/symbols/[symbol]` with
  accessible name `{symbol} daily OHLC chart`.
- Docs: ADR-0006; architecture overview and frontend README updates for Phase 5.

#### Explicitly out of scope

Backend API/schema changes, technical indicators, scoring/recommendations/signals, auth
changes, order placement, and NAS deployment - each is absent, not merely unimplemented, per
the Phase 5 plan.

### Phase 4 - Operator Authentication

Cookie-based operator sessions protect watchlist and market-data HTTP routes. No scoring,
recommendation, prediction, chart libraries, OAuth/MFA, multi-role RBAC, or order-placement
logic exists in this phase; see
[docs/architecture/decisions/0005-phase-4-operator-auth.md](docs/architecture/decisions/0005-phase-4-operator-auth.md).

#### Added

- Backend auth: `operators` table (Alembic migration `0004`); Argon2 password hashes; Redis
  session store with httpOnly cookie (`AEGIS_SESSION_*`); `POST /auth/login`,
  `POST /auth/logout`, `GET /auth/me`; session dependency on `/watchlist*` and
  `/market-data*`; seed-once bootstrap from `AEGIS_OPERATOR_USERNAME` /
  `AEGIS_OPERATOR_PASSWORD` when the operators table is empty; CORS
  `allow_credentials=True` with the existing origin allow-list. `/health` and `/ready` remain
  public.
- Frontend: `/login` page; API client `credentials: "include"`; 401 redirects to login;
  `requireOperator` SSR gate on protected console routes; logout clears the session.
- Configuration and docs: operator/session settings in `.env.example` and
  [docs/operations/configuration.md](docs/operations/configuration.md); ADR-0005;
  local-development login and migration notes.

#### Explicitly out of scope

OAuth/SSO, MFA, password-reset email, multi-role authorization, charts/scoring/recommendations,
order placement, and NAS deployment - each is absent, not merely unimplemented, per the
Phase 4 plan.

### Phase 3 - Operator Console (Frontend)

A browser operator console for the existing Phase 1/2 APIs: manage the watchlist, trigger
on-demand ingest, and browse stored daily bars as a table. No scoring, recommendation,
prediction, chart libraries, authentication, or order-placement logic exists in this phase;
see
[docs/architecture/decisions/0004-phase-3-operator-console.md](docs/architecture/decisions/0004-phase-3-operator-console.md).

#### Added

- Frontend console (`frontend/`): `/` watchlist + ingest panels; `/symbols/[symbol]` daily-bar
  table; Source Sans 3 / IBM Plex Mono typography; typed API client extensions for watchlist,
  ingest, and daily bars; Vitest coverage for the client and key components.
- Backend CORS: `AEGIS_CORS_ORIGINS` setting and `CORSMiddleware` so the Next.js origin can call
  the API from the browser; Compose passes the setting through; unit tests cover allow-listed
  vs rejected preflight origins.

#### Explicitly out of scope

Authentication, chart libraries/indicators/scoring, schedule configuration UI, second
providers, corrections, and NAS deployment - each is absent, not merely unimplemented, per the
Phase 3 plan.

### Phase 2 - Scheduled Ingestion & Database-Backed Watchlist

Ingestion now runs automatically on a schedule, and the watchlist moves from a static
environment variable to a database-backed list manageable via the API while the service is
running. No scoring, recommendation, prediction, or order-placement logic exists anywhere in
this phase; see
[docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md](docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md)
for the confirmed decisions (scheduler, coordination lock, watchlist storage, bootstrap,
validation, auth) and their accepted limitations.

#### Added

- Domain layer (`backend/src/aegis/domain/`): `watchlist.py` (`normalize_symbol`, a
  framework-free shape validator for user-submitted symbols) and `scheduled_ingestion.py`
  (`run_locked_ingestion_cycle`, a framework-free, `Protocol`-based lock-guarded ingestion
  cycle - independently unit-tested with fake Redis/watchlist/ingestion-service doubles, no
  real I/O).
- Persistence (`backend/src/aegis/persistence/`): `WatchlistSymbol` model and
  `WatchlistRepository` (`list_active`, `list_active_rows`, `add`, `deactivate`,
  `ensure_seeded`), plus an Alembic migration (`0003`) creating `watchlist_symbols` as a plain
  (non-hypertable) table with a unique constraint on `symbol`. Unlike
  `market_daily_bar_observations`, this table is a mutable, soft-deletable operational list,
  not an append-only observation (see ADR-0003).
- API (`backend/src/aegis/api/`): `GET /watchlist`, `POST /watchlist`, and
  `DELETE /watchlist/{symbol}` for watchlist management; `POST /market-data/ingest` now reads
  the active database-backed watchlist instead of `AEGIS_WATCHLIST_SYMBOLS` directly.
  `scheduler.py` wires an APScheduler `AsyncIOScheduler` into the application lifespan, running
  `run_locked_ingestion_cycle` on a cron schedule (`AEGIS_INGESTION_CRON`) guarded by a Redis
  lock (`AEGIS_INGESTION_SCHEDULE_LOCK_KEY`/`_TTL_SECONDS`) so multiple backend replicas can
  never run overlapping cycles; disabled entirely via `AEGIS_INGESTION_SCHEDULE_ENABLED=false`.
- Configuration: `AEGIS_INGESTION_SCHEDULE_ENABLED`, `AEGIS_INGESTION_CRON`,
  `AEGIS_INGESTION_SCHEDULE_LOCK_KEY`, `AEGIS_INGESTION_SCHEDULE_LOCK_TTL_SECONDS`, documented
  in `.env.example` and `docs/operations/configuration.md`. `AEGIS_WATCHLIST_SYMBOLS`'s role
  changes from "the watchlist" to "the one-time bootstrap seed" for the database table.
- Unit tests for symbol validation, the locked scheduled-ingestion cycle (fake doubles, no real
  I/O), the watchlist endpoints (dependency overrides), and scheduler lifespan wiring
  (enabled/disabled); a new cross-service integration test
  (`tests/integration/test_watchlist_repository_docker.py`) verifying the migration and the
  repository's add/deactivate/reactivate/seed behavior against the real Compose Postgres
  service.
- `apscheduler` added as a new main runtime dependency.

#### Explicitly out of scope

Any scoring/probability/confidence/recommendation computation, order placement/transmission,
frontend changes, authentication on any endpoint, a second data provider or intraday
granularity, and a separate worker process or multi-replica-aware scheduling beyond the Redis
lock - each is absent, not merely unimplemented, per the Phase 2 plan.

### Phase 1 - Market Data Ingestion (Alpha Vantage daily bars)

The first real external data integration: a typed Alpha Vantage provider adapter, validated
daily-bar rejection rules, an append-only TimescaleDB observation store, and on-demand
ingest/read API endpoints. No scoring, recommendation, prediction, or order-placement logic
exists anywhere in this phase; see
[docs/architecture/decisions/0002-phase-1-market-data-ingestion.md](docs/architecture/decisions/0002-phase-1-market-data-ingestion.md)
for the confirmed decisions (provider, granularity, trigger, watchlist, calendar, auth,
idempotency) and their accepted limitations.

#### Added

- Provider adapter (`backend/src/aegis/providers/`): `DailyBarProvider` protocol,
  `AlphaVantageProvider` (Alpha Vantage `TIME_SERIES_DAILY`, unadjusted daily OHLCV), and typed
  `ProviderError`/`ProviderRateLimitError` for both HTTP failures and Alpha Vantage's
  "200 OK with an error body" responses (invalid symbol, rate limit, premium-tier gate).
- Domain layer (`backend/src/aegis/domain/`): a swappable exchange-calendar wrapper
  (`calendars.py`, backed by `pandas-market-calendars`); daily-bar validation
  (`market_data_validation.py`) implementing every rejection rule from
  `docs/architecture/market-data-contracts.md` (invalid OHLC shape, non-positive values,
  closed-session/non-trading-day, and latest-bar staleness); and `MarketDataIngestionService`
  (`market_data_ingestion.py`) orchestrating fetch, validate, and idempotent persistence per
  watchlist symbol, isolating one symbol's provider failure from the rest of the run.
- Persistence (`backend/src/aegis/persistence/`): `MarketDailyBarObservation` model and
  `MarketDailyBarRepository`, plus an Alembic migration creating
  `market_daily_bar_observations` as a TimescaleDB hypertable (partitioned on `event_time`)
  with a unique constraint on `(source, symbol, event_time)` for idempotent re-ingestion.
- API (`backend/src/aegis/api/`): `POST /market-data/ingest` (runs one ingestion cycle over the
  configured watchlist) and `GET /market-data/{symbol}/daily-bars` (reads stored bars, 404 for
  an unknown symbol). No authentication in Phase 1 (self-hosted, local/trusted-network only;
  see ADR-0002).
- Configuration: `AEGIS_ALPHA_VANTAGE_API_KEY`, `AEGIS_ALPHA_VANTAGE_BASE_URL`,
  `AEGIS_ALPHA_VANTAGE_REQUEST_INTERVAL_SECONDS`, `AEGIS_WATCHLIST_SYMBOLS`,
  `AEGIS_DAILY_BAR_OUTPUT_SIZE`, `AEGIS_EXCHANGE_CALENDAR_NAME`, and
  `AEGIS_MAX_LATEST_BAR_STALENESS_TRADING_DAYS`, documented in `.env.example` and
  `docs/operations/configuration.md`.
- Unit tests for the provider adapter (`httpx.MockTransport`), calendar wrapper, validation
  rules, ingestion orchestration (fake provider/repository doubles, no real I/O), and both API
  endpoints (dependency overrides); a new cross-service integration test
  (`tests/integration/test_market_data_repository_docker.py`) verifying the migration,
  hypertable, and idempotent insert/read round trip against the real Compose Postgres/
  TimescaleDB service.
- `httpx` promoted from a test-only to a main runtime dependency; `pandas-market-calendars`
  added as a new main runtime dependency.

#### Explicitly out of scope

Order placement/transmission, any scoring/probability/confidence/recommendation computation,
background/scheduled ingestion, authentication on the new endpoints, a database-backed
watchlist, and any frontend change - each is absent, not merely unimplemented, per the Phase 1
plan.

### Phase 0 - Architecture & Repository Foundation

Repository and architecture foundation. No scoring, recommendation, prediction, or order-
placement logic exists anywhere in this phase; see
[docs/architecture/decisions/0001-phase-0-tooling.md](docs/architecture/decisions/0001-phase-0-tooling.md)
for the tooling decisions and
[docs/operations/](docs/operations/) for operational documentation.

#### Added

- Architecture documentation: system overview, data-model conventions (append-only,
  versioned, provenance-aware observations; coverage vs. probability confidence;
  research-only vs. actionable state), and market-data quote-rejection contracts.
- Backend service (`backend/`): FastAPI application on Python 3.12 managed with `uv`, exposing
  `/health` (liveness) and `/ready` (readiness against PostgreSQL/TimescaleDB and Redis), a
  baseline Alembic migration enabling the TimescaleDB extension, unit tests, and a scoped
  no-domain-logic structural check.
- Frontend service (`frontend/`): Next.js + TypeScript + Tailwind CSS application managed with
  pnpm, a single placeholder page, a typed API client for the backend health contract, and an
  equivalent no-domain-logic check.
- Local Docker Compose topology (`docker-compose.yml`) with health-checked `postgres`, `redis`,
  `backend`, and `frontend` services, plus pinned, non-root Dockerfiles for the backend and
  frontend and a build-only `linux/amd64` validation step for the UGREEN NAS target
  architecture (`docker/nas/README.md` documents the deployment boundary; no deployment occurs).
- Cross-service integration test (`tests/integration/`) verifying the readiness endpoint against
  the real Compose stack.
- CI workflow (`.github/workflows/ci.yml`) with backend, frontend, compose-validation,
  integration, and security-scanning jobs, and documentation of which gates are local-only vs.
  remote-dependent (`docs/operations/ci.md`).
- Security scanning documentation and local commands for dependency (`pip-audit`, `pnpm audit`),
  secret (`gitleaks`), and container-image (`trivy`) scans (`docs/operations/security-scanning.md`).
- Environment configuration reference (`.env.example`, `docs/operations/configuration.md`) and
  day-to-day developer workflow documentation (`docs/operations/local-development.md`).
- `.gitleaks.toml` allowlisting vendored/build directories for local secret scanning.

#### Fixed

- Backend: bumped `pytest`/`pytest-asyncio` to remediate a `pytest` CVE
  (`PYSEC-2026-1845`).
- Frontend: pinned `sharp` and `postcss` to patched versions via `pnpm-workspace.yaml`
  `overrides` (both are transitive `next` dependencies, not direct dependencies) to remediate
  `GHSA-f88m-g3jw-g9cj`, `GHSA-6g55-p6wh-862q`, `GHSA-r28c-9q8g-f849`, and
  `GHSA-qx2v-qp2m-jg93`.
- Docker images: both Dockerfiles now run `apt-get upgrade` in the final stage to pick up
  Debian security patches published after the pinned base image tag; the frontend image also
  removes the unused, bundled `npm`/`npx` CLI (this image only ever runs `node server.js`),
  eliminating scanner findings for code that is never executed. Both images scan clean at
  `trivy image --severity HIGH,CRITICAL --ignore-unfixed` as of this entry.
