# NAS Live Verification Checklist (Phase 17 + Phase 21 + Phase 23)

This checklist is the operator evidence gate after package/deploy. Architecture:
[ADR-0018](../architecture/decisions/0018-phase-17-nas-live-verification.md),
[ADR-0022](../architecture/decisions/0022-phase-21-nas-live-verify-phases-18-20.md),
[ADR-0024](../architecture/decisions/0024-phase-23-nas-live-verify-phase-22.md).
Authoritative scripted checks: `docker/nas/scripts/verify.ps1` / `verify.sh`.

**Upload ≠ verified.** Dry-run mode is **not** acceptance evidence.

## Before verify

1. Local Phase acceptance gates passed for the revision you deployed.
2. `.env.nas` filled (not placeholders) with SSH, public URLs, and strong operator password.
3. `package` and `deploy` completed for that revision (`alembic upgrade head` on start).
   On aarch64 NAS hosts, a native on-NAS `docker compose build` is an acceptable packaging
   path when workstation cross-build is impractical.
4. Optional TLS: `AEGIS_NAS_TLS_ENABLED=true`, HTTPS verify URLs, Secure cookies.

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
| 3 | Unauthenticated watchlist / daily-bars / research latest / calibration-readiness / **evidence-summary** | 401 |
| 4 | Frontend base URL | 200 / 302 / 307 / 308 |
| 5 | `POST /auth/login` (uses `.env.nas` operator credentials) | 200 + session cookie |
| 6 | Authenticated `GET /research/{symbol}/calibration-readiness` | 200 |
| 7 | Authenticated `GET /research/{symbol}/assessments/latest` | 200 or **404** (empty history OK) |
| 8 | Authenticated `GET .../assessments/{id}/calibrations` and `.../outcome-labels` | **200** JSON array (`[]` OK) |
| 9 | Authenticated `GET /research/{symbol}/evidence-summary` | **200**, `state=research_only` |
| 10 | SSH `alembic current` (when SSH configured) | includes **`0008`** or `head` |
| 11 | TLS (if enabled) | HTTPS URLs + `AEGIS_SESSION_COOKIE_SECURE=true` |

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
