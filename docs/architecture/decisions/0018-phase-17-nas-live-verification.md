# ADR-0018: Phase 17 NAS Live Verification (Ops Evidence Gate)

- Status: Accepted
- Date: 2026-07-29

## Context

Phases 0–16 delivered a research-only local stack through calibration readiness diagnostics.
Phase 7 packaged NAS Compose overlays and package/deploy/verify scripts; Phase 9 added
optional TLS. Project rules treat **package upload** and **verified live deployment** as
distinct. Phase 17 hardens the **verify** evidence gate for the current revision without
expanding product capabilities (no actionable promotion, orders, or default-on calibration).

## Decisions

### 1. What “live verified” means

A revision is **live verified** on a NAS only when `docker/nas/scripts/verify`
(PowerShell or shell) completes successfully against the operator-facing origins in
gitignored `.env.nas`. Success requires:

| Check | Expectation |
| --- | --- |
| `GET /health` | 200 |
| `GET /ready` | 200 |
| Auth gate without session on watchlist, daily-bars, research latest, **calibration-readiness** | 401 |
| Frontend base URL | 200 or redirect |
| Operator login (`POST /auth/login`) when credentials are present in `.env.nas` | 200 + session cookie |
| Authenticated `GET /research/{symbol}/calibration-readiness` | 200 |
| Authenticated `GET /research/{symbol}/assessments/latest` | 200 or 404 (no snapshot yet is allowed) |
| `alembic current` via SSH when SSH vars are set | includes **`0008`** or `head` |
| TLS profile (when enabled) | `https://` verify URLs + `AEGIS_SESSION_COOKIE_SECURE=true` |

Upload, `docker compose up`, or packaging alone is **not** live verification.

### 2. Dry-run mode (not live evidence)

`verify.ps1 -DryRun` / `verify.sh --dry-run` prints the checklist and exits 0 **without**
contacting the NAS. Dry-run output must be labeled so it cannot be mistaken for acceptance
evidence.

### 3. Symbol under test

Optional `AEGIS_NAS_VERIFY_SYMBOL` (default `AAPL`) selects the symbol used for research
and calibration-readiness checks. No market-data ingest is required for the auth gate;
authenticated latest assessment may be 404 when the corpus is empty.

### 4. Calibration remains opt-in

Verify does **not** require `AEGIS_RESEARCH_CALIBRATION_AFTER_LABEL_ENABLED=true`. Readiness
diagnostics must succeed (HTTP 200) even when calibration is disabled.

### 5. Documentation

Operator checklist lives in `docs/operations/nas-live-verification.md` and
`docker/nas/README.md`. Evidence format: paste verify script stdout (live run, not dry-run).

## Consequences

- Operators have an explicit, revision-aware verify gate covering Phase 16 readiness routes
  and migrations through `0008`.
- Local unit tests remain separate from NAS live evidence.

## Explicitly out of scope

- Changing calibration default to enabled
- Actionable promotion, recommendations, orders
- New product features or scoring methods
- Automating NAS hardware provisioning

## Related documents

- [0008-phase-7-nas-deployment.md](0008-phase-7-nas-deployment.md)
- [0010-phase-9-nas-tls-reverse-proxy.md](0010-phase-9-nas-tls-reverse-proxy.md)
- [0017-phase-16-calibration-readiness.md](0017-phase-16-calibration-readiness.md)
- [../../operations/nas-live-verification.md](../../operations/nas-live-verification.md)
- [../../../docker/nas/README.md](../../../docker/nas/README.md)
