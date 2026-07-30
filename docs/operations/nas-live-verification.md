# NAS Live Verification Checklist (Phase 17 + Phase 21 + Phase 23 + Phase 25 + Phase 27 + Phase 29 + Phase 31 + Phase 33 + Phase 35 + Phase 37 + Phase 39 + Phase 42 + Phase 44 + Phase 46 + Phase 48 + Phase 50 + Phase 52)

This checklist is the operator evidence gate after package/deploy. Architecture:
[ADR-0018](../architecture/decisions/0018-phase-17-nas-live-verification.md),
[ADR-0022](../architecture/decisions/0022-phase-21-nas-live-verify-phases-18-20.md),
[ADR-0024](../architecture/decisions/0024-phase-23-nas-live-verify-phase-22.md),
[ADR-0026](../architecture/decisions/0026-phase-25-nas-live-verify-phase-24.md),
[ADR-0028](../architecture/decisions/0028-phase-27-nas-live-verify-phase-26.md),
[ADR-0030](../architecture/decisions/0030-phase-29-nas-live-verify-phase-28.md),
[ADR-0032](../architecture/decisions/0032-phase-31-nas-live-verify-phase-30.md),
[ADR-0034](../architecture/decisions/0034-phase-33-nas-live-verify-phase-32.md),
[ADR-0036](../architecture/decisions/0036-phase-35-nas-live-verify-phase-34.md),
[ADR-0038](../architecture/decisions/0038-phase-37-nas-live-verify-phase-36.md),
[ADR-0040](../architecture/decisions/0040-phase-39-nas-live-verify-phase-38.md),
[ADR-0041](../architecture/decisions/0041-phase-40-nas-lab-tls-cutover.md),
[ADR-0043](../architecture/decisions/0043-phase-42-nas-live-verify-phase-41.md),
[ADR-0045](../architecture/decisions/0045-phase-44-nas-live-verify-phase-43.md),
[ADR-0047](../architecture/decisions/0047-phase-46-nas-live-verify-phase-45.md),
[ADR-0049](../architecture/decisions/0049-phase-48-nas-live-verify-phase-47.md),
[ADR-0051](../architecture/decisions/0051-phase-50-nas-live-verify-phase-49.md),
[ADR-0053](../architecture/decisions/0053-phase-52-nas-live-verify-phase-51.md).
Authoritative scripted checks: `docker/nas/scripts/verify.ps1` / `verify.sh`.
Lab TLS cutover/rollback: [nas-tls-cutover.md](nas-tls-cutover.md).

**Upload ≠ verified.** Dry-run mode is **not** acceptance evidence.

## Before verify

1. Local Phase acceptance gates passed for the revision you deployed.
2. `.env.nas` filled (not placeholders) with SSH, public URLs, and strong operator password.
3. For Phase 52+, ensure ``AEGIS_RESEARCH_BAR_LOAD_LIMIT=252`` (or higher within bounds) is set
   in `.env.nas` before recreate (ADR-0053).
4. `package` and `deploy` completed for that revision (`alembic upgrade head` on start).
   On aarch64 NAS hosts, a native on-NAS `docker compose build` is an acceptable packaging
   path when workstation cross-build is impractical.
5. Optional TLS: `AEGIS_NAS_TLS_ENABLED=true`, HTTPS verify URLs, Secure cookies.

## Run live verify

```powershell
.\docker\nas\scripts\verify.ps1
```

```sh
./docker/nas/scripts/verify.sh
```

Optional symbol (default `AAPL`):

```powershell
$env:AEGIS_NAS_VERIFY_SYMBOL = "MSFT"
.\docker\nas\scripts\verify.ps1
```

## Expected checks (must all pass)

| # | Check | Pass criteria |
| --- | --- | --- |
| 1 | `GET {API}/health` | 200 |
| 2 | `GET {API}/ready` | 200 |
| 3 | Unauthenticated watchlist / daily-bars / research latest / assessments list(+**export**) / calibration-readiness(+export) / outcome-labels/export / calibrations/export / evidence-summary(+export) / **outcome-labels/backfill POST** / **assessments/backfill POST** | 401 |
| 4 | Frontend base URL | 200 / 302 / 307 / 308 |
| 5 | `POST /auth/login` (uses `.env.nas` operator credentials) | 200 + session cookie |
| 6 | Authenticated `GET /research/{symbol}/calibration-readiness` | **200**, `by_horizon` includes `forward_return_5` and `forward_return_20` |
| 7 | Authenticated `GET /research/{symbol}/calibration-readiness/export` | **200**, attachment, readiness `status` + `by_horizon` present |
| 8 | Authenticated `GET /research/{symbol}/assessments/latest` | 200 or **404** (empty history OK) |
| 9 | Authenticated `GET /research/{symbol}/assessments?limit=` | **200** JSON array (`[]` OK) |
| 10 | Authenticated `GET /research/{symbol}/assessments/export` | **200**, attachment, JSON array (`[]` OK) |
| 11 | Authenticated `POST /research/{symbol}/assessments/backfill?limit=` | **200**, summary counts present (zeros / skips OK; Phase 52 prefers new persists when deeper stored bars unlock candidates) |
| 12 | Authenticated `POST /research/{symbol}/outcome-labels/backfill?limit=` | **200**, summary counts present; if step 11 `persisted_count > 0` then labels `persisted_count >= 1` (Phase 49 prefers unlabeled label-ready candidates) |
| 13 | Authenticated `POST .../assessments/{id}/calibrations?horizon=forward_return_5` | **200** or fail-closed **422** |
| 14 | Authenticated `GET .../assessments/{id}/calibrations` and `.../outcome-labels` | **200** JSON array (`[]` OK) |
| 15 | Authenticated `GET .../assessments/{id}/outcome-labels/export` | **200**, attachment, JSON array (`[]` OK) |
| 16 | Authenticated `GET .../assessments/{id}/calibrations/export` | **200**, attachment, JSON array (`[]` OK) |
| 17 | Authenticated `GET /research/{symbol}/evidence-summary` | **200**, `state=research_only`; log present label/end-date keys only (none OK) |
| 18 | Authenticated `GET /research/{symbol}/evidence-summary/export` | **200**, attachment, `state=research_only` |
| 19 | SSH `alembic current` (when SSH configured) | includes **`0009`** or `head` |
| 20 | SSH `.env.nas` `AEGIS_RESEARCH_BAR_LOAD_LIMIT` (Phase 52) | present and in **40–2000** |
| 21 | TLS (if enabled) | HTTPS URLs + `AEGIS_SESSION_COOKIE_SECURE=true` |

Capture stdout as evidence. Failures exit non-zero — do not mark the NAS revision verified.

## Dry-run (planning only)

```powershell
.\docker\nas\scripts\verify.ps1 -DryRun
```

```sh
./docker/nas/scripts/verify.sh --dry-run
```

Prints the checklist without contacting the NAS. **Not** live verification evidence.

## After verify

Inspect logs if needed (script prints guidance when SSH is configured):

```sh
docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml \
  --env-file .env.nas --project-directory . logs --tail=200 backend
```

Keep `AEGIS_RESEARCH_CALIBRATION_AFTER_LABEL_ENABLED=false` until readiness shows
`ready` for your symbols and you intentionally opt in.
