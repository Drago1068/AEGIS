# NAS Live Verification Checklist (Phase 17 + Phase 21 + Phase 23 + Phase 25 + Phase 27 + Phase 29 + Phase 31 + Phase 33 + Phase 35 + Phase 37 + Phase 39 + Phase 42 + Phase 44 + Phase 46 + Phase 48 + Phase 50 + Phase 52 + Phase 54 + Phase 56 + Phase 58 + Phase 60)

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
[ADR-0053](../architecture/decisions/0053-phase-52-nas-live-verify-phase-51.md),
[ADR-0055](../architecture/decisions/0055-phase-54-nas-live-verify-phase-53.md),
[ADR-0057](../architecture/decisions/0057-phase-56-nas-live-verify-phase-55.md),
[ADR-0059](../architecture/decisions/0059-phase-58-nas-live-verify-phase-57.md),
[ADR-0061](../architecture/decisions/0061-phase-60-nas-live-verify-phase-59.md),
[ADR-0073](../architecture/decisions/0073-phase-72-nas-live-verify-phase-71.md),
[ADR-0075](../architecture/decisions/0075-phase-74-nas-live-verify-phase-73.md),
[ADR-0076](../architecture/decisions/0076-phase-75-evidence-summary-by-horizon-verify.md),
[ADR-0077](../architecture/decisions/0077-phase-76-evidence-summary-corpus-bucket-verify.md),
[ADR-0079](../architecture/decisions/0079-phase-78-nas-live-verify-phase-77.md),
[ADR-0081](../architecture/decisions/0081-phase-80-nas-live-verify-phase-79.md),
[ADR-0083](../architecture/decisions/0083-phase-82-nas-live-verify-phase-81.md),
[ADR-0085](../architecture/decisions/0085-phase-84-nas-live-verify-phase-83.md),
[ADR-0087](../architecture/decisions/0087-phase-86-nas-live-verify-phase-85.md),
[ADR-0089](../architecture/decisions/0089-phase-88-nas-live-verify-phase-87.md),
[ADR-0091](../architecture/decisions/0091-phase-90-nas-live-verify-phase-89.md),
[ADR-0093](../architecture/decisions/0093-phase-92-nas-live-verify-phase-91.md),
[ADR-0095](../architecture/decisions/0095-phase-94-nas-live-verify-phase-93.md),
[ADR-0097](../architecture/decisions/0097-phase-96-nas-live-verify-phase-95.md),
[ADR-0099](../architecture/decisions/0099-phase-98-nas-live-verify-phase-97.md),
[ADR-0101](../architecture/decisions/0101-phase-100-nas-live-verify-phase-99.md),
[ADR-0103](../architecture/decisions/0103-phase-102-nas-live-verify-phase-101.md),
[ADR-0105](../architecture/decisions/0105-phase-104-nas-live-verify-phase-103.md),
[ADR-0107](../architecture/decisions/0107-phase-106-nas-live-verify-phase-105.md),
[ADR-0109](../architecture/decisions/0109-phase-108-nas-live-verify-phase-107.md).
Authoritative scripted checks: `docker/nas/scripts/verify.ps1` / `verify.sh`.
Lab TLS cutover/rollback: [nas-tls-cutover.md](nas-tls-cutover.md).

**Upload ≠ verified.** Dry-run mode is **not** acceptance evidence.

## Before verify

1. Local Phase acceptance gates passed for the revision you deployed.
2. `.env.nas` filled (not placeholders) with SSH, public URLs, and strong operator password.
3. For Phase 52+, ensure ``AEGIS_RESEARCH_BAR_LOAD_LIMIT=252`` (or higher within bounds) is set
   in `.env.nas` before recreate (ADR-0053).
4. For Phase 54+, ensure ``AEGIS_DAILY_BAR_OUTPUT_SIZE=full`` is set, recreate the backend, and
   re-run authenticated ingest so stored bars can grow beyond compact depth (ADR-0055).
5. For Phase 56+, ensure ``AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=true`` is set and
   the Phase 55 session-depth research load is deployed (ADR-0057).
6. For Phase 58+, deploy Phase 57 source-aware label backfill (ADR-0059).
7. `package` and `deploy` completed for that revision (`alembic upgrade head` on start).
   On aarch64 NAS hosts, a native on-NAS `docker compose build` is an acceptable packaging
   path when workstation cross-build is impractical.
8. Optional TLS: `AEGIS_NAS_TLS_ENABLED=true`, HTTPS verify URLs, Secure cookies.

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
| 21 | SSH `.env.nas` `AEGIS_DAILY_BAR_OUTPUT_SIZE` (Phase 54) | **`full`** |
| 22 | SSH `.env.nas` `AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL` (Phase 56) | **`true`** |
| 23 | Authenticated `POST .../outcome-labels/backfill?limit=100` (Phase 58) | **200**; persist when source-ready candidates exist |
| 24 | Authenticated evidence-summary provenance (Phase 60) | ``latest_component_source``, ``latest_resolved_label_bar_source``, ``mixed_component_source_assessment_count`` present |
| 25 | Authenticated assessments list+export ``component_source=mixed`` (Phase 62) | **200**; rows resolve to mixed; non-empty when evidence mixed_count > 0 |
| 26 | Phase 64 frontend redeploy (Phase 63 one-click mixed filter) | Frontend recreated; one-click UX unit-tested; API path covered by item 25 |
| 27 | Phase 66 backend redeploy (Phase 65 prefer-mixed label backfill) | Backend recreated; ``outcome-labels/backfill?limit=100`` **200** |
| 28 | Authenticated evidence-summary mixed label coverage (Phase 68) | ``mixed_unlabeled_assessment_count``, ``latest_mixed_label_bar_source`` present |
| 29 | Authenticated evidence-summary mixed labeled count (Phase 70) | ``mixed_labeled_assessment_count`` present; labeled+unlabeled == mixed count |
| 30 | Phase 72 frontend redeploy (Phase 71 corpus callout) | Frontend recreated; corpus UI unit-tested; nested readiness fields on summary |
| 31 | Phase 74 frontend redeploy (Phase 73 by_horizon rows) | Frontend recreated; by_horizon UI unit-tested; nested readiness retained |
| 32 | Authenticated evidence-summary nested ``by_horizon`` (Phase 75) | ``calibration_readiness.by_horizon`` includes ``forward_return_5`` + ``forward_return_20`` (+ export) |
| 33 | Authenticated evidence-summary nested corpus/bucket (Phase 76) | ``corpus_count``, ``min_corpus``, ``bucket_count``, ``min_bucket`` present with bounds (+ export) |
| 34 | Phase 78 frontend redeploy (Phase 77 horizon detail expand) | Frontend recreated; expand UX unit-tested |
| 35 | Authenticated evidence-summary most_recent_labeled_* (Phase 80) | ``most_recent_labeled_assessment_id`` + ``most_recent_labeled_outcome_label`` present (+ export; null OK) |
| 36 | Phase 82 frontend redeploy (Phase 81 load-scan-labeled) | Frontend recreated; load-labels UX unit-tested |
| 37 | Phase 84 frontend redeploy (Phase 83 assessment-id caption) | Frontend recreated; caption UX unit-tested |
| 38 | Phase 86 frontend redeploy (Phase 85 load-kind caption) | Frontend recreated; load-kind UX unit-tested |
| 39 | Phase 88 frontend redeploy (Phase 87 download loaded assessment) | Frontend recreated; download UX unit-tested |
| 40 | Phase 90 frontend redeploy (Phase 89 download names assessment) | Frontend recreated; named-download UX unit-tested |
| 41 | Phase 92 frontend redeploy (Phase 91 empty-state loaded assessment) | Frontend recreated; empty-state UX unit-tested |
| 42 | Phase 94 frontend redeploy (Phase 93 compute loaded assessment) | Frontend recreated; compute UX unit-tested |
| 43 | Phase 96 frontend redeploy (Phase 95 backfill refresh loaded assessment) | Frontend recreated; backfill refresh UX unit-tested |
| 44 | Phase 98 frontend redeploy (Phase 97 assessment backfill preserves labels) | Frontend recreated; preserve UX unit-tested |
| 45 | Phase 100 frontend redeploy (Phase 99 calibrations download names latest) | Frontend recreated; named-calibrations UX unit-tested |
| 46 | Phase 102 frontend redeploy (Phase 101 compute calibration names latest) | Frontend recreated; named-compute UX unit-tested |
| 47 | Phase 104 frontend redeploy (Phase 103 calibration note scan-labeled) | Frontend recreated; note UX unit-tested |
| 48 | Phase 106 frontend redeploy (Phase 105 load labels for latest) | Frontend recreated; load-latest UX unit-tested |
| 49 | Phase 108 frontend redeploy (Phase 107 active assessment id rename) | Frontend recreated; rename covered by unit tests |
| 50 | Phase 110 frontend redeploy (Phase 109 handlers use active assessment id) | Frontend recreated; handler single-source covered by unit tests |
| 51 | Phase 112 frontend redeploy (Phase 111 resolve load-kind helper) | Frontend recreated; load-kind helper covered by unit tests |
| 52 | Phase 114 frontend redeploy (Phase 113 outcome-label aria load-kind) | Frontend recreated; aria load-kind UX unit-tested |
| 53 | Phase 116 frontend redeploy (Phase 115 extract helpers module) | Frontend recreated; helpers module covered by unit tests |
| 54 | Phase 118 frontend redeploy (Phase 117 outcome-label id-chip load-kind) | Frontend recreated; id-chip load-kind UX unit-tested |
| 55 | Phase 120 frontend redeploy (Phase 119 calibration chips name latest) | Frontend recreated; calibration chip UX unit-tested |
| 56 | Phase 122 frontend redeploy (Phase 121 backfill names refresh target) | Frontend recreated; backfill naming UX unit-tested |
| 57 | Phase 124 frontend redeploy (Phase 123 extract action toolbar) | Frontend recreated; toolbar extract covered by unit tests |
| 58 | Phase 126 frontend redeploy (Phase 125 group action toolbar) | Frontend recreated; toolbar grouping UX unit-tested |
| 59 | Phase 128 frontend redeploy (Phase 127 extract outcome-label history section) | Frontend recreated; section extract covered by unit tests |
| 60 | Phase 130 frontend redeploy (Phase 129 extract assessment history section) | Frontend recreated; section extract covered by unit tests |
| 61 | Phase 132 frontend redeploy (Phase 131 extract calibration readiness section) | Frontend recreated; section extract covered by unit tests |
| 62 | Phase 134 frontend redeploy (Phase 133 extract probability calibration section) | Frontend recreated; section extract covered by unit tests |
| 63 | Phase 136 frontend redeploy (Phase 135 extract evidence summary section) | Frontend recreated; section extract covered by unit tests |
| 64 | Phase 138 frontend redeploy (Phase 137 extract latest assessment detail section) | Frontend recreated; section extract covered by unit tests |
| 65 | Phase 140 frontend redeploy (Phase 139 extract backfill status banners) | Frontend recreated; section extract covered by unit tests |
| 66 | Phase 142 frontend redeploy (Phase 141 extract panel header) | Frontend recreated; header extract covered by unit tests |
| 67 | Phase 144 frontend redeploy (Phase 143 extract error alert) | Frontend recreated; error alert extract covered by unit tests |
| 68 | Phase 146 backend+frontend redeploy (Phase 145 scan label counts) | Evidence-summary includes labeled_assessment_count + unlabeled_assessment_count |
| 69 | Phase 148 backend+frontend redeploy (Phase 147 latest coverage confidence) | Evidence-summary includes latest_coverage_confidence (null OK) |
| 70 | Phase 150 backend+frontend redeploy (Phase 149 latest research index) | Evidence-summary includes latest_research_index (null OK) |
| 71 | Phase 152 backend+frontend redeploy (Phase 151 latest as-of date) | Evidence-summary includes latest_as_of_trading_date (null OK) |
| 72 | Phase 154 backend+frontend redeploy (Phase 153 latest bar count) | Evidence-summary includes latest_bar_count (null OK) |
| 73 | Phase 156 backend+frontend redeploy (Phase 155 latest input source) | Evidence-summary includes latest_input_source (null OK) |
| 74 | Phase 158 backend+frontend redeploy (Phase 157 latest method id) | Evidence-summary includes latest_method_id (null OK) |
| 75 | Phase 160 backend+frontend redeploy (Phase 159 latest method version) | Evidence-summary includes latest_method_version (null OK) |
| 76 | Phase 162 backend+frontend redeploy (Phase 161 latest lookback end) | Evidence-summary includes latest_lookback_end_date (null OK) |
| 77 | Phase 164 backend+frontend redeploy (Phase 163 latest lookback start) | Evidence-summary includes latest_lookback_start_date (null OK) |
| 78 | Phase 166 backend+frontend redeploy (Phase 165 latest schema version) | Evidence-summary includes latest_schema_version (null OK) |
| 79 | Phase 168 backend+frontend redeploy (Phase 167 latest computed_at) | Evidence-summary includes latest_computed_at (null OK) |
| 80 | Phase 170 backend+frontend redeploy (Phase 169 latest event_time) | Evidence-summary includes latest_event_time (null OK) |
| 81 | Phase 172 backend+frontend redeploy (Phase 171 latest probability confidence) | Evidence-summary includes latest_probability_confidence (null OK) |
| 82 | Phase 174 backend+frontend redeploy (Phase 173 latest assessment id) | Evidence-summary includes latest_assessment_id (null OK) |
| 83 | Phase 176 backend+frontend redeploy (Phase 175 latest outcome label id) | Evidence-summary includes latest_outcome_label_id (null OK) |
| 84 | Phase 178 backend+frontend redeploy (Phase 177 latest calibration id) | Evidence-summary includes latest_calibration_id (null OK) |
| 85 | Phase 180 backend+frontend redeploy (Phase 179 latest calibration horizon) | Evidence-summary includes latest_calibration_horizon_key (null OK) |
| 86 | Phase 182 backend+frontend redeploy (Phase 181 latest calibration computed_at) | Evidence-summary includes latest_calibration_computed_at (null OK) |
| 87 | Phase 184 backend+frontend redeploy (Phase 183 latest calibration corpus) | Evidence-summary includes latest_calibration_corpus_count (null OK) |
| 88 | Phase 186 backend+frontend redeploy (Phase 185 latest calibration bucket) | Evidence-summary includes latest_calibration_bucket_count (null OK) |
| 89 | Phase 188 backend+frontend redeploy (Phase 187 latest calibration method id) | Evidence-summary includes latest_calibration_method_id (null OK) |
| 90 | Phase 190 backend+frontend redeploy (Phase 189 latest calibration method version) | Evidence-summary includes latest_calibration_method_version (null OK) |
| 91 | Phase 192 backend+frontend redeploy (Phase 191 latest calibration schema version) | Evidence-summary includes latest_calibration_schema_version (null OK) |
| 92 | Phase 194 backend+frontend redeploy (Phase 193 latest calibration state) | Evidence-summary includes latest_calibration_state (null OK) |
| 93 | Phase 196 backend+frontend redeploy (Phase 195 latest calibration probability confidence) | Evidence-summary includes latest_calibration_probability_confidence (null OK) |
| 94 | Phase 198 backend+frontend redeploy (Phase 197 latest calibration assessment snapshot id) | Evidence-summary includes latest_calibration_assessment_snapshot_id (null OK) |
| 95 | Phase 200 backend+frontend redeploy (Phase 199 latest outcome label computed_at) | Evidence-summary includes latest_outcome_label_computed_at (null OK) |
| 96 | Phase 202 backend+frontend redeploy (Phase 201 latest outcome label method id) | Evidence-summary includes latest_outcome_label_method_id (null OK) |
| 97 | Phase 204 backend+frontend redeploy (Phase 203 latest outcome label method version) | Evidence-summary includes latest_outcome_label_method_version (null OK) |
| 98 | Phase 206 backend+frontend redeploy (Phase 205 latest outcome label schema version) | Evidence-summary includes latest_outcome_label_schema_version (null OK) |
| 99 | Phase 208 backend+frontend redeploy (Phase 207 latest outcome label state) | Evidence-summary includes latest_outcome_label_state (null OK) |
| 100 | Phase 210 backend+frontend redeploy (Phase 209 latest outcome label bar source) | Evidence-summary includes latest_outcome_label_bar_source (null OK) |
| 101 | Phase 212 backend+frontend redeploy (Phase 211 latest outcome label as-of trading date) | Evidence-summary includes latest_outcome_label_as_of_trading_date (null OK) |
| 102 | Phase 214 backend+frontend redeploy (Phase 213 most recent labeled outcome label id) | Evidence-summary includes most_recent_labeled_outcome_label_id (null OK when no scan labels) |
| 103 | Phase 216 backend+frontend redeploy (Phase 215 most recent labeled outcome label method id) | Evidence-summary includes most_recent_labeled_outcome_label_method_id (null OK when no scan labels) |
| 104 | Phase 218 backend+frontend redeploy (Phase 217 most recent labeled outcome label method version) | Evidence-summary includes most_recent_labeled_outcome_label_method_version (null OK when no scan labels) |
| 105 | Phase 220 backend+frontend redeploy (Phase 219 most recent labeled outcome label schema version) | Evidence-summary includes most_recent_labeled_outcome_label_schema_version (null OK when no scan labels) |
| 106 | Phase 222 backend+frontend redeploy (Phase 221 most recent labeled outcome label state) | Evidence-summary includes most_recent_labeled_outcome_label_state (null OK when no scan labels) |
| 107 | Phase 224 backend+frontend redeploy (Phase 223 most recent labeled outcome label bar source) | Evidence-summary includes most_recent_labeled_outcome_label_bar_source (null OK when no scan labels) |
| 108 | Phase 226 backend+frontend redeploy (Phase 225 most recent labeled outcome label computed_at) | Evidence-summary includes most_recent_labeled_outcome_label_computed_at (null OK when no scan labels) |
| 109 | Phase 228 backend+frontend redeploy (Phase 227 most recent labeled outcome label as-of trading date) | Evidence-summary includes most_recent_labeled_outcome_label_as_of_trading_date (null OK when no scan labels) |
| 110 | Phase 230 backend+frontend redeploy (Phase 229 scan-labeled freshness lag) | Evidence-summary includes scan_labeled_freshness_lag_trading_days (null OK when either as_of missing) |
| 111 | Phase 232 backend+frontend redeploy (Phase 231 latest assessment is label ready) | Evidence-summary includes latest_assessment_is_label_ready (null OK when no assessment) |
| 112 | Phase 234 backend+frontend redeploy (Phase 233 latest assessment label block reason) | Evidence-summary includes latest_assessment_label_block_reason (null OK when ready / no assessment) |
| 113 | Phase 236 backend+frontend redeploy (Phase 235 most recent labelable as-of) | Evidence-summary includes most_recent_labelable_as_of_trading_date (null OK when none label-ready) |
| 114 | Phase 238 backend+frontend redeploy (Phase 237 most recent unlabeled labelable as-of) | Evidence-summary includes most_recent_unlabeled_labelable_as_of_trading_date (null OK when none) |
| 115 | Phase 240 backend+frontend redeploy (Phase 239 scan unlabeled label-ready count) | Evidence-summary includes scan_unlabeled_label_ready_count (0 OK when none) |
| 116 | Phase 242 backend+frontend redeploy (Phase 241 most recent unlabeled assessment id) | Evidence-summary includes most_recent_unlabeled_assessment_id (null OK when none unlabeled) |
| 117 | Phase 244 backend+frontend redeploy (Phase 243 most recent unlabeled as-of) | Evidence-summary includes most_recent_unlabeled_as_of_trading_date (null OK when none unlabeled) |
| 118 | Phase 246 backend+frontend redeploy (Phase 245 latest forward bar shortfall) | Evidence-summary includes latest_assessment_forward_bar_shortfall (null/0 OK) |
| 119 | Phase 248 backend+frontend redeploy (Phase 247 required label end date) | Evidence-summary includes latest_assessment_required_label_end_date (null OK) |
| 120 | Phase 250 backend+frontend redeploy (Phase 249 last available label bar date) | Evidence-summary includes latest_assessment_last_available_label_bar_date (null OK) |
| 121 | Phase 252 backend+frontend redeploy (Phase 251 min-horizon forward bar shortfall) | Evidence-summary includes latest_assessment_min_horizon_forward_bar_shortfall (null/0 OK) |
| 122 | Phase 254 backend+frontend redeploy (Phase 253 min-horizon required label end date) | Evidence-summary includes latest_assessment_min_horizon_required_label_end_date (null OK) |
| 123 | Phase 256 backend+frontend redeploy (Phase 255 stored-bar calendar lag) | Evidence-summary includes stored_bar_calendar_lag_trading_days (null/0 OK) |
| 124 | Phase 258–260 on-demand ingest tip refresh + provider tip | Authenticated POST /market-data/ingest + latest_trading_date + re-read lag/tip (unchanged OK) |
| 125 | TLS (if enabled) | HTTPS URLs + `AEGIS_SESSION_COOKIE_SECURE=true` |

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
