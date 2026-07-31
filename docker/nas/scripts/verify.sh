#!/usr/bin/env bash
# Verify a live AEGIS NAS deployment (Phase 7/9 + Phase 17 evidence gate).
# Distinct from package upload / deploy start.
# Usage: ./docker/nas/scripts/verify.sh [--dry-run]
# See docs/architecture/decisions/0018-phase-17-nas-live-verification.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
ENV_NAS="${REPO_ROOT}/.env.nas"
DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
fi

VERIFY_SYMBOL="AAPL"
if [[ -f "${ENV_NAS}" ]]; then
  load_dotenv_file "${ENV_NAS}"
  if [[ -n "${AEGIS_NAS_VERIFY_SYMBOL:-}" ]]; then
    VERIFY_SYMBOL="$(printf '%s' "${AEGIS_NAS_VERIFY_SYMBOL}" | tr '[:lower:]' '[:upper:]')"
  fi
fi

print_checklist() {
  local symbol="$1"
  echo "Live verification checklist (ADR-0018):"
  echo "  1. GET /health -> 200"
  echo "  2. GET /ready -> 200"
  echo "  3. Auth gate 401: watchlist, daily-bars, research latest, assessments list(+export), calibration-readiness(+export), outcome-labels/export, calibrations/export, evidence-summary(+export), outcome-labels/backfill POST, assessments/backfill POST"
  echo "  4. Frontend base URL -> 200|302|307|308"
  echo "  5. POST /auth/login (operator credentials from .env.nas) -> 200 + cookie"
  echo "  6. Authenticated GET /research/${symbol}/calibration-readiness -> 200 (by_horizon includes fwd5+fwd20)"
  echo "  7. Authenticated GET /research/${symbol}/calibration-readiness/export -> 200 (attachment; by_horizon present)"
  echo "  8. Authenticated GET /research/${symbol}/assessments/latest -> 200|404"
  echo "  9. Authenticated GET /research/${symbol}/assessments?limit= -> 200 (JSON array; [] OK)"
  echo " 10. Authenticated GET /research/${symbol}/assessments/export -> 200 (attachment, JSON array; [] OK)"
  echo " 11. Authenticated POST /research/${symbol}/assessments/backfill -> 200 (summary counts; zeros OK)"
  echo " 12. Authenticated POST /research/${symbol}/outcome-labels/backfill -> 200 (summary counts; if assessments persisted>0 then labels persisted>=1)"
  echo " 13. Authenticated POST .../assessments/{id}/calibrations?horizon=forward_return_5 -> 200|422"
  echo " 14. Authenticated GET .../assessments/{id}/calibrations and .../outcome-labels -> 200 (JSON array; [] OK)"
  echo " 15. Authenticated GET .../assessments/{id}/outcome-labels/export -> 200 (attachment, JSON array; [] OK)"
  echo " 16. Authenticated GET .../assessments/{id}/calibrations/export -> 200 (attachment, JSON array; [] OK)"
  echo " 17. Authenticated GET /research/${symbol}/evidence-summary -> 200 (state=research_only; log present label + end-date keys when any)"
  echo " 18. Authenticated GET /research/${symbol}/evidence-summary/export -> 200 (attachment, state=research_only)"
  echo " 19. SSH alembic current includes 0009|head (when SSH configured)"
  echo " 20. SSH .env.nas includes AEGIS_RESEARCH_BAR_LOAD_LIMIT in bounds (Phase 52)"
  echo " 21. SSH .env.nas includes AEGIS_DAILY_BAR_OUTPUT_SIZE=full (Phase 54)"
  echo " 22. SSH .env.nas includes AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=true (Phase 56)"
  echo " 23. Authenticated POST outcome-labels/backfill?limit=100 (Phase 58 source-aware throughput)"
  echo " 24. Authenticated evidence-summary includes Phase 59 provenance fields"
  echo " 25. Authenticated assessments list+export with component_source=mixed (Phase 62)"
  echo " 26. Phase 64: frontend redeploy includes Phase 63 one-click mixed filter (unit-tested; API via item 25)"
  echo " 27. Phase 66: backend redeploy includes Phase 65 prefer-mixed label backfill (limit=100 path)"
  echo " 28. Authenticated evidence-summary includes Phase 67 mixed label coverage fields"
  echo " 29. Authenticated evidence-summary includes Phase 69 mixed_labeled_assessment_count (Phase 70)"
  echo " 30. Phase 72: frontend redeploy includes Phase 71 corpus callout (unit-tested; readiness nested fields)"
  echo " 31. Phase 74: frontend redeploy includes Phase 73 by_horizon mini-rows (unit-tested; nested readiness)"
  echo " 32. Authenticated evidence-summary nested calibration_readiness.by_horizon includes fwd5+fwd20 (Phase 75)"
  echo " 33. Authenticated evidence-summary nested corpus/bucket readiness fields (Phase 76)"
  echo " 34. Phase 78: frontend redeploy includes Phase 77 horizon detail expand (unit-tested)"
  echo " 35. Authenticated evidence-summary most_recent_labeled_* fields (Phase 80)"
  echo " 36. Phase 82: frontend redeploy includes Phase 81 load-scan-labeled control (unit-tested)"
  echo " 37. Phase 84: frontend redeploy includes Phase 83 assessment-id caption (unit-tested)"
  echo " 38. Phase 86: frontend redeploy includes Phase 85 load-kind caption (unit-tested)"
  echo " 39. Phase 88: frontend redeploy includes Phase 87 download-loaded-assessment (unit-tested)"
  echo " 40. Phase 90: frontend redeploy includes Phase 89 download-names-assessment (unit-tested)"
  echo " 41. Phase 92: frontend redeploy includes Phase 91 empty-state-loaded-assessment (unit-tested)"
  echo " 42. Phase 94: frontend redeploy includes Phase 93 compute-loaded-assessment (unit-tested)"
  echo " 43. Phase 96: frontend redeploy includes Phase 95 backfill-refresh-loaded-assessment (unit-tested)"
  echo " 44. Phase 98: frontend redeploy includes Phase 97 assessment-backfill-preserves-labels (unit-tested)"
  echo " 45. Phase 100: frontend redeploy includes Phase 99 calibrations-download-names-latest (unit-tested)"
  echo " 46. Phase 102: frontend redeploy includes Phase 101 compute-calibration-names-latest (unit-tested)"
  echo " 47. Phase 104: frontend redeploy includes Phase 103 calibration-note-scan-labeled (unit-tested)"
  echo " 48. Phase 106: frontend redeploy includes Phase 105 load-labels-for-latest (unit-tested)"
  echo " 49. Phase 108: frontend redeploy includes Phase 107 active-assessment-id-rename (unit-tested)"
  echo " 50. Phase 110: frontend redeploy includes Phase 109 handlers-use-active-assessment-id (unit-tested)"
  echo " 51. Phase 112: frontend redeploy includes Phase 111 resolve-outcome-label-load-kind (unit-tested)"
  echo " 52. Phase 114: frontend redeploy includes Phase 113 outcome-label-aria-load-kind (unit-tested)"
  echo " 53. Phase 116: frontend redeploy includes Phase 115 extract-outcome-label-helpers (unit-tested)"
  echo " 54. Phase 118: frontend redeploy includes Phase 117 outcome-label-id-chip-load-kind (unit-tested)"
  echo " 55. Phase 120: frontend redeploy includes Phase 119 calibration-chips-name-latest (unit-tested)"
  echo " 56. Phase 122: frontend redeploy includes Phase 121 backfill-names-refresh-target (unit-tested)"
  echo " 57. Phase 124: frontend redeploy includes Phase 123 extract-action-toolbar (unit-tested)"
  echo " 58. Phase 126: frontend redeploy includes Phase 125 group-action-toolbar (unit-tested)"
  echo " 59. Phase 128: frontend redeploy includes Phase 127 extract-outcome-label-history-section (unit-tested)"
  echo " 60. Phase 130: frontend redeploy includes Phase 129 extract-assessment-history-section (unit-tested)"
  echo " 61. Phase 132: frontend redeploy includes Phase 131 extract-calibration-readiness-section (unit-tested)"
  echo " 62. Phase 134: frontend redeploy includes Phase 133 extract-probability-calibration-section (unit-tested)"
  echo " 63. Phase 136: frontend redeploy includes Phase 135 extract-evidence-summary-section (unit-tested)"
  echo " 64. Phase 138: frontend redeploy includes Phase 137 extract-latest-assessment-section (unit-tested)"
  echo " 65. Phase 140: frontend redeploy includes Phase 139 extract-backfill-status-section (unit-tested)"
  echo " 66. Phase 142: frontend redeploy includes Phase 141 extract-panel-header (unit-tested)"
  echo " 67. Phase 144: frontend redeploy includes Phase 143 extract-error-alert (unit-tested)"
  echo " 68. Authenticated evidence-summary includes Phase 145 labeled/unlabeled scan counts (Phase 146)"
  echo " 69. Authenticated evidence-summary includes Phase 147 latest_coverage_confidence (Phase 148)"
  echo " 70. Authenticated evidence-summary includes Phase 149 latest_research_index (Phase 150)"
  echo " 71. Authenticated evidence-summary includes Phase 151 latest_as_of_trading_date (Phase 152)"
  echo " 72. Authenticated evidence-summary includes Phase 153 latest_bar_count (Phase 154)"
  echo " 73. Authenticated evidence-summary includes Phase 155 latest_input_source (Phase 156)"
  echo " 74. Authenticated evidence-summary includes Phase 157 latest_method_id (Phase 158)"
  echo " 75. Authenticated evidence-summary includes Phase 159 latest_method_version (Phase 160)"
  echo " 76. Authenticated evidence-summary includes Phase 161 latest_lookback_end_date (Phase 162)"
  echo " 77. Authenticated evidence-summary includes Phase 163 latest_lookback_start_date (Phase 164)"
  echo " 78. Authenticated evidence-summary includes Phase 165 latest_schema_version (Phase 166)"
  echo " 79. Authenticated evidence-summary includes Phase 167 latest_computed_at (Phase 168)"
  echo " 80. Authenticated evidence-summary includes Phase 169 latest_event_time (Phase 170)"
  echo " 81. Authenticated evidence-summary includes Phase 171 latest_probability_confidence (Phase 172)"
  echo " 82. Authenticated evidence-summary includes Phase 173 latest_assessment_id (Phase 174)"
  echo " 83. Authenticated evidence-summary includes Phase 175 latest_outcome_label_id (Phase 176)"
  echo " 84. Authenticated evidence-summary includes Phase 177 latest_calibration_id (Phase 178)"
  echo " 85. Authenticated evidence-summary includes Phase 179 latest_calibration_horizon_key (Phase 180)"
  echo " 86. Authenticated evidence-summary includes Phase 181 latest_calibration_computed_at (Phase 182)"
  echo " 87. Authenticated evidence-summary includes Phase 183 latest_calibration_corpus_count (Phase 184)"
  echo " 88. Authenticated evidence-summary includes Phase 185 latest_calibration_bucket_count (Phase 186)"
  echo " 89. Authenticated evidence-summary includes Phase 187 latest_calibration_method_id (Phase 188)"
  echo " 90. Authenticated evidence-summary includes Phase 189 latest_calibration_method_version (Phase 190)"
  echo " 91. Authenticated evidence-summary includes Phase 191 latest_calibration_schema_version (Phase 192)"
  echo " 92. Authenticated evidence-summary includes Phase 193 latest_calibration_state (Phase 194)"
  echo " 93. Authenticated evidence-summary includes Phase 195 latest_calibration_probability_confidence (Phase 196)"
  echo " 94. Authenticated evidence-summary includes Phase 197 latest_calibration_assessment_snapshot_id (Phase 198)"
  echo " 95. TLS profile: https:// URLs + Secure cookies when enabled"
}

if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "==> DRY RUN — checklist only; NOT live verification evidence"
  print_checklist "${VERIFY_SYMBOL}"
  echo
  echo "Dry-run complete. Run without --dry-run against a live NAS for acceptance evidence."
  exit 0
fi

require_env_vars \
  AEGIS_NAS_API_BASE_URL \
  AEGIS_NAS_FRONTEND_BASE_URL \
  AEGIS_OPERATOR_USERNAME \
  AEGIS_OPERATOR_PASSWORD

API="${AEGIS_NAS_API_BASE_URL%/}"
FRONTEND="${AEGIS_NAS_FRONTEND_BASE_URL%/}"

if [[ "${API}" == *replace-with-* || "${FRONTEND}" == *replace-with-* ]]; then
  echo "error: AEGIS_NAS_API_BASE_URL / AEGIS_NAS_FRONTEND_BASE_URL still look like placeholders." >&2
  exit 1
fi
if [[ "${AEGIS_OPERATOR_PASSWORD}" == *replace-with-* || "${AEGIS_OPERATOR_PASSWORD}" == *change-me-before-non-local-use* ]]; then
  echo "error: AEGIS_OPERATOR_PASSWORD still looks like a template placeholder." >&2
  exit 1
fi

if nas_tls_enabled; then
  if [[ "${API}" != https://* || "${FRONTEND}" != https://* ]]; then
    echo "error: TLS profile requires https:// verify URLs (API=${API}, FRONTEND=${FRONTEND})." >&2
    exit 1
  fi
  secure="$(printf '%s' "${AEGIS_SESSION_COOKIE_SECURE:-}" | tr '[:upper:]' '[:lower:]')"
  if [[ "${secure}" != "true" && "${secure}" != "1" ]]; then
    echo "error: TLS profile requires AEGIS_SESSION_COOKIE_SECURE=true." >&2
    exit 1
  fi
  echo "==> TLS profile enabled — verifying over HTTPS"
fi

CURL_INSECURE=()
insecure="$(printf '%s' "${AEGIS_NAS_VERIFY_CURL_INSECURE:-false}" | tr '[:upper:]' '[:lower:]')"
if [[ "${insecure}" == "true" || "${insecure}" == "1" || "${insecure}" == "yes" ]]; then
  echo "NOTE: AEGIS_NAS_VERIFY_CURL_INSECURE set — curl will skip TLS certificate verification (lab only)."
  CURL_INSECURE=(-k)
fi
if [[ -n "${AEGIS_NAS_VERIFY_CURL_RESOLVE:-}" ]]; then
  IFS=',' read -r -a _resolve_entries <<< "${AEGIS_NAS_VERIFY_CURL_RESOLVE}"
  for entry in "${_resolve_entries[@]}"; do
    entry="$(printf '%s' "${entry}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    if [[ -n "${entry}" ]]; then
      CURL_INSECURE+=(--resolve "${entry}")
    fi
  done
  echo "NOTE: AEGIS_NAS_VERIFY_CURL_RESOLVE set — curl --resolve overrides for lab DNS."
fi

http_status() {
  local url="$1"
  local cookie_jar="${2:-}"
  if [[ -n "${cookie_jar}" ]]; then
    curl -sS "${CURL_INSECURE[@]}" -o /dev/null -w "%{http_code}" --max-time 30 -b "${cookie_jar}" "${url}"
  else
    curl -sS "${CURL_INSECURE[@]}" -o /dev/null -w "%{http_code}" --max-time 30 "${url}"
  fi
}

assert_status() {
  local label="$1"
  local actual="$2"
  shift 2
  local expected=("$@")
  local ok=0
  local e
  for e in "${expected[@]}"; do
    if [[ "${actual}" == "${e}" ]]; then
      ok=1
      break
    fi
  done
  if [[ "${ok}" -ne 1 ]]; then
    echo "error: ${label}: expected HTTP ${expected[*]}, got ${actual}" >&2
    exit 1
  fi
  echo "OK  ${label} -> ${actual}"
}

print_checklist "${VERIFY_SYMBOL}"
echo

echo "==> Public health and readiness"
assert_status "GET ${API}/health" "$(http_status "${API}/health")" 200
assert_status "GET ${API}/ready" "$(http_status "${API}/ready")" 200

echo "==> Auth gate (expect 401 without session)"
assert_status "GET ${API}/watchlist" "$(http_status "${API}/watchlist")" 401
assert_status "GET ${API}/market-data/${VERIFY_SYMBOL}/daily-bars" "$(http_status "${API}/market-data/${VERIFY_SYMBOL}/daily-bars")" 401
assert_status "GET ${API}/research/${VERIFY_SYMBOL}/assessments/latest" "$(http_status "${API}/research/${VERIFY_SYMBOL}/assessments/latest")" 401
assert_status "GET ${API}/research/${VERIFY_SYMBOL}/assessments" "$(http_status "${API}/research/${VERIFY_SYMBOL}/assessments")" 401
assert_status "GET ${API}/research/${VERIFY_SYMBOL}/assessments/export" "$(http_status "${API}/research/${VERIFY_SYMBOL}/assessments/export")" 401
assert_status "GET ${API}/research/${VERIFY_SYMBOL}/calibration-readiness" "$(http_status "${API}/research/${VERIFY_SYMBOL}/calibration-readiness")" 401
assert_status "GET ${API}/research/${VERIFY_SYMBOL}/calibration-readiness/export" "$(http_status "${API}/research/${VERIFY_SYMBOL}/calibration-readiness/export")" 401
assert_status "GET ${API}/research/${VERIFY_SYMBOL}/assessments/1/outcome-labels/export" "$(http_status "${API}/research/${VERIFY_SYMBOL}/assessments/1/outcome-labels/export")" 401
assert_status "GET ${API}/research/${VERIFY_SYMBOL}/assessments/1/calibrations/export" "$(http_status "${API}/research/${VERIFY_SYMBOL}/assessments/1/calibrations/export")" 401
assert_status "GET ${API}/research/${VERIFY_SYMBOL}/evidence-summary" "$(http_status "${API}/research/${VERIFY_SYMBOL}/evidence-summary")" 401
assert_status "GET ${API}/research/${VERIFY_SYMBOL}/evidence-summary/export" "$(http_status "${API}/research/${VERIFY_SYMBOL}/evidence-summary/export")" 401
backfill_unauth_url="${API}/research/${VERIFY_SYMBOL}/outcome-labels/backfill?limit=20"
backfill_unauth_code="$(
  curl -sS "${CURL_INSECURE[@]}" -o /dev/null -w "%{http_code}" --max-time 30 \
    -H "Accept: application/json" -X POST "${backfill_unauth_url}"
)"
assert_status "POST ${backfill_unauth_url} (unauth)" "${backfill_unauth_code}" 401
assess_backfill_unauth_url="${API}/research/${VERIFY_SYMBOL}/assessments/backfill?limit=20"
assess_backfill_unauth_code="$(
  curl -sS "${CURL_INSECURE[@]}" -o /dev/null -w "%{http_code}" --max-time 30 \
    -H "Accept: application/json" -X POST "${assess_backfill_unauth_url}"
)"
assert_status "POST ${assess_backfill_unauth_url} (unauth)" "${assess_backfill_unauth_code}" 401

echo "==> Frontend reachability"
fe_status="$(http_status "${FRONTEND}")"
assert_status "GET ${FRONTEND}" "${fe_status}" 200 307 308 302

echo "==> Operator login + authenticated research diagnostics"
COOKIE_JAR="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}"; }
trap cleanup EXIT

login_code="$(
  curl -sS "${CURL_INSECURE[@]}" -o /dev/null -w "%{http_code}" --max-time 30 \
    -c "${COOKIE_JAR}" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d "{\"username\":\"${AEGIS_OPERATOR_USERNAME}\",\"password\":\"${AEGIS_OPERATOR_PASSWORD}\"}" \
    "${API}/auth/login"
)"
assert_status "POST ${API}/auth/login" "${login_code}" 200

ready_code="$(http_status "${API}/research/${VERIFY_SYMBOL}/calibration-readiness" "${COOKIE_JAR}")"
assert_status "GET ${API}/research/${VERIFY_SYMBOL}/calibration-readiness (auth)" "${ready_code}" 200

ready_body="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_body}"; }
trap cleanup EXIT
curl -sS "${CURL_INSECURE[@]}" -o "${ready_body}" --max-time 30 \
  -b "${COOKIE_JAR}" -H "Accept: application/json" \
  "${API}/research/${VERIFY_SYMBOL}/calibration-readiness" >/dev/null
if ! grep -q '"by_horizon"' "${ready_body}"; then
  echo "calibration-readiness missing by_horizon" >&2
  exit 1
fi
if ! grep -q 'forward_return_5' "${ready_body}" || ! grep -q 'forward_return_20' "${ready_body}"; then
  echo "calibration-readiness by_horizon missing forward_return_5/20" >&2
  exit 1
fi
echo "OK  calibration-readiness by_horizon includes forward_return_5 and forward_return_20"

ready_export_url="${API}/research/${VERIFY_SYMBOL}/calibration-readiness/export"
ready_export_body="$(mktemp)"
ready_export_headers="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_body}" "${ready_export_body}" "${ready_export_headers}"; }
trap cleanup EXIT
ready_export_code="$(
  curl -sS "${CURL_INSECURE[@]}" -D "${ready_export_headers}" -o "${ready_export_body}" -w "%{http_code}" --max-time 30 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" "${ready_export_url}"
)"
assert_status "GET ${ready_export_url} (auth)" "${ready_export_code}" 200
if ! grep -qi 'content-disposition:.*attachment' "${ready_export_headers}"; then
  echo "calibration-readiness/export missing Content-Disposition attachment" >&2
  exit 1
fi
if ! grep -q '"status"' "${ready_export_body}"; then
  echo "calibration-readiness/export missing status" >&2
  exit 1
fi
if ! grep -q '"by_horizon"' "${ready_export_body}"; then
  echo "calibration-readiness/export missing by_horizon" >&2
  exit 1
fi
echo "OK  calibration-readiness/export attachment"

latest_code="$(http_status "${API}/research/${VERIFY_SYMBOL}/assessments/latest" "${COOKIE_JAR}")"
assert_status "GET ${API}/research/${VERIFY_SYMBOL}/assessments/latest (auth)" "${latest_code}" 200 404

assess_list_url="${API}/research/${VERIFY_SYMBOL}/assessments?limit=20"
assess_body="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_body}" "${ready_export_body}" "${ready_export_headers}" "${assess_body}"; }
trap cleanup EXIT
assess_code="$(
  curl -sS "${CURL_INSECURE[@]}" -o "${assess_body}" -w "%{http_code}" --max-time 30 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" "${assess_list_url}"
)"
assert_status "GET ${assess_list_url} (auth)" "${assess_code}" 200
if ! head -c 1 "${assess_body}" | grep -q '\['; then
  echo "assessments list body is not a JSON array" >&2
  exit 1
fi
echo "OK  assessments list is JSON array"

assess_export_url="${API}/research/${VERIFY_SYMBOL}/assessments/export?limit=20"
assess_export_body="$(mktemp)"
assess_export_headers="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_export_body}" "${ready_export_headers}" "${assess_body}" "${assess_export_body}" "${assess_export_headers}"; }
trap cleanup EXIT
assess_export_code="$(
  curl -sS "${CURL_INSECURE[@]}" -D "${assess_export_headers}" -o "${assess_export_body}" -w "%{http_code}" --max-time 30 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" "${assess_export_url}"
)"
assert_status "GET ${assess_export_url} (auth)" "${assess_export_code}" 200
if ! grep -qi 'content-disposition:.*attachment' "${assess_export_headers}"; then
  echo "assessments/export missing Content-Disposition attachment" >&2
  exit 1
fi
if ! head -c 1 "${assess_export_body}" | grep -q '\['; then
  echo "assessments/export body is not a JSON array" >&2
  exit 1
fi
echo "OK  assessments/export attachment JSON array"

mixed_list_url="${API}/research/${VERIFY_SYMBOL}/assessments?limit=20&component_source=mixed"
mixed_list_body="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_export_body}" "${ready_export_headers}" "${assess_body}" "${assess_export_body}" "${assess_export_headers}" "${mixed_list_body}"; }
trap cleanup EXIT
mixed_list_code="$(
  curl -sS "${CURL_INSECURE[@]}" -o "${mixed_list_body}" -w "%{http_code}" --max-time 60 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" "${mixed_list_url}"
)"
assert_status "GET ${mixed_list_url} (auth)" "${mixed_list_code}" 200
if ! head -c 1 "${mixed_list_body}" | grep -q '\['; then
  echo "assessments?component_source=mixed body is not a JSON array" >&2
  exit 1
fi
mixed_list_count="$(python3 -c "import json,sys; print(len(json.load(open(sys.argv[1],encoding='utf-8'))))" "${mixed_list_body}")"
python3 -c "
import json, sys
rows = json.load(open(sys.argv[1], encoding='utf-8'))
for row in rows:
    comps = row.get('components') or {}
    src = comps.get('component_source') or row.get('input_source')
    if src != 'mixed':
        raise SystemExit(f\"non-mixed row id={row.get('id')} src={src}\")
" "${mixed_list_body}"
echo "OK  assessments?component_source=mixed JSON array (count=${mixed_list_count})"

mixed_export_url="${API}/research/${VERIFY_SYMBOL}/assessments/export?limit=20&component_source=mixed"
mixed_export_body="$(mktemp)"
mixed_export_headers="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_export_body}" "${ready_export_headers}" "${assess_body}" "${assess_export_body}" "${assess_export_headers}" "${mixed_list_body}" "${mixed_export_body}" "${mixed_export_headers}"; }
trap cleanup EXIT
mixed_export_code="$(
  curl -sS "${CURL_INSECURE[@]}" -D "${mixed_export_headers}" -o "${mixed_export_body}" -w "%{http_code}" --max-time 60 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" "${mixed_export_url}"
)"
assert_status "GET ${mixed_export_url} (auth)" "${mixed_export_code}" 200
if ! grep -qi 'content-disposition:.*attachment' "${mixed_export_headers}"; then
  echo "assessments/export?component_source=mixed missing Content-Disposition attachment" >&2
  exit 1
fi
if ! head -c 1 "${mixed_export_body}" | grep -q '\['; then
  echo "assessments/export?component_source=mixed body is not a JSON array" >&2
  exit 1
fi
echo "OK  assessments/export?component_source=mixed attachment JSON array"
echo "OK  Phase 62 assessments component_source=mixed list+export"

assess_backfill_url="${API}/research/${VERIFY_SYMBOL}/assessments/backfill?limit=20"
assess_backfill_body="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_body}" "${ready_export_body}" "${ready_export_headers}" "${assess_body}" "${assess_export_body}" "${assess_export_headers}" "${assess_backfill_body}"; }
trap cleanup EXIT
assess_backfill_code="$(
  curl -sS "${CURL_INSECURE[@]}" -o "${assess_backfill_body}" -w "%{http_code}" --max-time 120 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" -X POST "${assess_backfill_url}"
)"
assert_status "POST ${assess_backfill_url} (auth)" "${assess_backfill_code}" 200
if ! grep -q '"candidate_count"' "${assess_backfill_body}" \
  || ! grep -q '"persisted_count"' "${assess_backfill_body}" \
  || ! grep -q '"skipped_count"' "${assess_backfill_body}"; then
  echo "assessments/backfill missing summary count fields" >&2
  exit 1
fi
assess_persisted="$(
  python3 -c 'import json,sys; print(int(json.load(open(sys.argv[1])).get("persisted_count") or 0))' \
    "${assess_backfill_body}"
)"
echo "OK  assessments/backfill summary counts present (persisted=${assess_persisted})"

backfill_url="${API}/research/${VERIFY_SYMBOL}/outcome-labels/backfill?limit=20"
backfill_body="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_body}" "${ready_export_body}" "${ready_export_headers}" "${assess_body}" "${assess_export_body}" "${assess_export_headers}" "${assess_backfill_body}" "${backfill_body}"; }
trap cleanup EXIT
backfill_code="$(
  curl -sS "${CURL_INSECURE[@]}" -o "${backfill_body}" -w "%{http_code}" --max-time 60 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" -X POST "${backfill_url}"
)"
assert_status "POST ${backfill_url} (auth)" "${backfill_code}" 200
if ! grep -q '"assessment_count"' "${backfill_body}" \
  || ! grep -q '"persisted_count"' "${backfill_body}" \
  || ! grep -q '"skipped_count"' "${backfill_body}"; then
  echo "outcome-labels/backfill missing summary count fields" >&2
  exit 1
fi
label_persisted="$(
  python3 -c 'import json,sys; print(int(json.load(open(sys.argv[1])).get("persisted_count") or 0))' \
    "${backfill_body}"
)"
echo "OK  outcome-labels/backfill summary counts present (persisted=${label_persisted})"
if [[ "${assess_persisted}" -gt 0 && "${label_persisted}" -lt 1 ]]; then
  echo "Phase 48: assessments/backfill persisted=${assess_persisted} but outcome-labels/backfill persisted=${label_persisted} (expected >=1 for label-ready candidates)" >&2
  exit 1
fi
if [[ "${assess_persisted}" -gt 0 ]]; then
  echo "OK  Phase 48/50 label-ready coupling at limit=20 (assessments persisted=${assess_persisted} -> labels persisted=${label_persisted})"
else
  echo "OK  Phase 48/50 label-ready coupling skipped (assessments persisted=0; label zeros OK)"
fi

backfill100_url="${API}/research/${VERIFY_SYMBOL}/outcome-labels/backfill?limit=100"
backfill100_body="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_body}" "${ready_export_body}" "${ready_export_headers}" "${assess_body}" "${assess_export_body}" "${assess_export_headers}" "${assess_backfill_body}" "${backfill_body}" "${backfill100_body}"; }
trap cleanup EXIT
backfill100_code="$(
  curl -sS "${CURL_INSECURE[@]}" -o "${backfill100_body}" -w "%{http_code}" --max-time 120 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" -X POST "${backfill100_url}"
)"
assert_status "POST ${backfill100_url} (auth)" "${backfill100_code}" 200
if ! grep -q '"assessment_count"' "${backfill100_body}" \
  || ! grep -q '"persisted_count"' "${backfill100_body}" \
  || ! grep -q '"skipped_count"' "${backfill100_body}"; then
  echo "outcome-labels/backfill?limit=100 missing summary count fields" >&2
  exit 1
fi
label100_assess="$(
  python3 -c 'import json,sys; print(int(json.load(open(sys.argv[1])).get("assessment_count") or 0))' \
    "${backfill100_body}"
)"
label100_persisted="$(
  python3 -c 'import json,sys; print(int(json.load(open(sys.argv[1])).get("persisted_count") or 0))' \
    "${backfill100_body}"
)"
label100_skipped="$(
  python3 -c 'import json,sys; print(int(json.load(open(sys.argv[1])).get("skipped_count") or 0))' \
    "${backfill100_body}"
)"
echo "OK  outcome-labels/backfill?limit=100 assessment_count=${label100_assess} persisted=${label100_persisted} skipped=${label100_skipped}"
if [[ "${label100_assess}" -gt 0 && "${label100_persisted}" -lt 1 ]]; then
  echo "Phase 58: limit=100 selected ${label100_assess} candidates but persisted=${label100_persisted} (expected >=1 when source-ready candidates exist)" >&2
  exit 1
fi
echo "OK  Phase 58 source-aware label backfill throughput check"
echo "OK  Phase 66 prefer-mixed label backfill path exercised (limit=100)"

history_assessment_id=1
if [[ "${latest_code}" == "200" ]]; then
  latest_json="$(
    curl -sS "${CURL_INSECURE[@]}" --max-time 30 \
      -b "${COOKIE_JAR}" -H "Accept: application/json" \
      "${API}/research/${VERIFY_SYMBOL}/assessments/latest"
  )"
  parsed_id="$(printf '%s' "${latest_json}" | sed -n 's/.*"id"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p' | head -n 1)"
  if [[ -n "${parsed_id}" ]]; then
    history_assessment_id="${parsed_id}"
  fi
fi

calib_post_url="${API}/research/${VERIFY_SYMBOL}/assessments/${history_assessment_id}/calibrations?horizon=forward_return_5"
calib_post_code="$(
  curl -sS "${CURL_INSECURE[@]}" -o /dev/null -w "%{http_code}" --max-time 30 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" -X POST "${calib_post_url}"
)"
assert_status "POST ${calib_post_url} (auth)" "${calib_post_code}" 200 422
echo "OK  POST calibrations?horizon=forward_return_5 -> ${calib_post_code} (200 or fail-closed 422)"

calib_list_url="${API}/research/${VERIFY_SYMBOL}/assessments/${history_assessment_id}/calibrations"
label_list_url="${API}/research/${VERIFY_SYMBOL}/assessments/${history_assessment_id}/outcome-labels"
calib_body="$(mktemp)"
label_body="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_export_body}" "${ready_export_headers}" "${assess_body}" "${assess_export_body}" "${assess_export_headers}" "${calib_body}" "${label_body}"; }
trap cleanup EXIT

calib_code="$(
  curl -sS "${CURL_INSECURE[@]}" -o "${calib_body}" -w "%{http_code}" --max-time 30 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" "${calib_list_url}"
)"
assert_status "GET ${calib_list_url} (auth)" "${calib_code}" 200
if ! head -c 1 "${calib_body}" | grep -q '\['; then
  echo "calibrations list body is not a JSON array" >&2
  exit 1
fi
echo "OK  calibrations list is JSON array"

label_code="$(
  curl -sS "${CURL_INSECURE[@]}" -o "${label_body}" -w "%{http_code}" --max-time 30 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" "${label_list_url}"
)"
assert_status "GET ${label_list_url} (auth)" "${label_code}" 200
if ! head -c 1 "${label_body}" | grep -q '\['; then
  echo "outcome-labels list body is not a JSON array" >&2
  exit 1
fi
echo "OK  outcome-labels list is JSON array"

label_export_url="${API}/research/${VERIFY_SYMBOL}/assessments/${history_assessment_id}/outcome-labels/export?limit=20"
label_export_body="$(mktemp)"
label_export_headers="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_export_body}" "${ready_export_headers}" "${assess_body}" "${assess_export_body}" "${assess_export_headers}" "${calib_body}" "${label_body}" "${label_export_body}" "${label_export_headers}"; }
trap cleanup EXIT
label_export_code="$(
  curl -sS "${CURL_INSECURE[@]}" -D "${label_export_headers}" -o "${label_export_body}" -w "%{http_code}" --max-time 30 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" "${label_export_url}"
)"
assert_status "GET ${label_export_url} (auth)" "${label_export_code}" 200
if ! grep -qi 'content-disposition:.*attachment' "${label_export_headers}"; then
  echo "outcome-labels/export missing Content-Disposition attachment" >&2
  exit 1
fi
if ! head -c 1 "${label_export_body}" | grep -q '\['; then
  echo "outcome-labels/export body is not a JSON array" >&2
  exit 1
fi
echo "OK  outcome-labels/export attachment JSON array"

calib_export_url="${API}/research/${VERIFY_SYMBOL}/assessments/${history_assessment_id}/calibrations/export?limit=20"
calib_export_body="$(mktemp)"
calib_export_headers="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_export_body}" "${ready_export_headers}" "${assess_body}" "${assess_export_body}" "${assess_export_headers}" "${calib_body}" "${label_body}" "${label_export_body}" "${label_export_headers}" "${calib_export_body}" "${calib_export_headers}"; }
trap cleanup EXIT
calib_export_code="$(
  curl -sS "${CURL_INSECURE[@]}" -D "${calib_export_headers}" -o "${calib_export_body}" -w "%{http_code}" --max-time 30 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" "${calib_export_url}"
)"
assert_status "GET ${calib_export_url} (auth)" "${calib_export_code}" 200
if ! grep -qi 'content-disposition:.*attachment' "${calib_export_headers}"; then
  echo "calibrations/export missing Content-Disposition attachment" >&2
  exit 1
fi
if ! head -c 1 "${calib_export_body}" | grep -q '\['; then
  echo "calibrations/export body is not a JSON array" >&2
  exit 1
fi
echo "OK  calibrations/export attachment JSON array"

summary_url="${API}/research/${VERIFY_SYMBOL}/evidence-summary"
summary_body="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_export_body}" "${ready_export_headers}" "${assess_body}" "${assess_export_body}" "${assess_export_headers}" "${calib_body}" "${label_body}" "${label_export_body}" "${label_export_headers}" "${calib_export_body}" "${calib_export_headers}" "${summary_body}"; }
trap cleanup EXIT
summary_code="$(
  curl -sS "${CURL_INSECURE[@]}" -o "${summary_body}" -w "%{http_code}" --max-time 30 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" "${summary_url}"
)"
assert_status "GET ${summary_url} (auth)" "${summary_code}" 200
if ! grep -q '"state"[[:space:]]*:[[:space:]]*"research_only"' "${summary_body}"; then
  echo "evidence-summary missing state=research_only" >&2
  exit 1
fi
if ! grep -q '"latest_component_source"' "${summary_body}"; then
  echo "evidence-summary missing latest_component_source (Phase 59/60)" >&2
  exit 1
fi
if ! grep -q '"latest_resolved_label_bar_source"' "${summary_body}"; then
  echo "evidence-summary missing latest_resolved_label_bar_source (Phase 59/60)" >&2
  exit 1
fi
if ! grep -q '"mixed_component_source_assessment_count"' "${summary_body}"; then
  echo "evidence-summary missing mixed_component_source_assessment_count (Phase 59/60)" >&2
  exit 1
fi
echo "OK  Phase 60 evidence-summary provenance fields present"
# Phase 62: when mixed assessments exist in the evidence scan, filtered list must be non-empty.
if grep -qE '"mixed_component_source_assessment_count"[[:space:]]*:[[:space:]]*[1-9]' "${summary_body}"; then
  if [[ "${mixed_list_count}" -lt 1 ]]; then
    echo "Phase 62: mixed_component_source_assessment_count>0 but assessments?component_source=mixed returned 0" >&2
    exit 1
  fi
  echo "OK  Phase 62 mixed filter non-empty when mixed_count>0 (filtered=${mixed_list_count})"
fi
# Phase 68: mixed label coverage fields from Phase 67.
if ! grep -q '"mixed_unlabeled_assessment_count"' "${summary_body}"; then
  echo "evidence-summary missing mixed_unlabeled_assessment_count (Phase 67/68)" >&2
  exit 1
fi
if ! grep -q '"latest_mixed_label_bar_source"' "${summary_body}"; then
  echo "evidence-summary missing latest_mixed_label_bar_source (Phase 67/68)" >&2
  exit 1
fi
echo "OK  Phase 68 mixed label coverage fields present"
if ! grep -q '"mixed_labeled_assessment_count"' "${summary_body}"; then
  echo "evidence-summary missing mixed_labeled_assessment_count (Phase 69/70)" >&2
  exit 1
fi
echo "OK  Phase 70 mixed labeled coverage field present"
# Phase 75: nested readiness by_horizon on evidence-summary (Phase 73 UI contract).
if ! grep -q '"by_horizon"' "${summary_body}"; then
  echo "evidence-summary.calibration_readiness missing by_horizon (Phase 75)" >&2
  exit 1
fi
if ! grep -q 'forward_return_5' "${summary_body}" || ! grep -q 'forward_return_20' "${summary_body}"; then
  echo "evidence-summary.calibration_readiness.by_horizon missing forward_return_5/20 (Phase 75)" >&2
  exit 1
fi
echo "OK  Phase 75 evidence-summary by_horizon includes forward_return_5 and forward_return_20"
# Phase 76: nested corpus/bucket fields for Phase 71 callout contract.
for field in corpus_count bucket_count min_corpus min_bucket; do
  if ! grep -q "\"${field}\"" "${summary_body}"; then
    echo "evidence-summary.calibration_readiness missing ${field} (Phase 76)" >&2
    exit 1
  fi
done
echo "OK  Phase 76 evidence-summary nested corpus/bucket readiness fields present"
# Phase 80: most-recent labeled fields from Phase 79 (null OK when none labeled).
if ! grep -q '"most_recent_labeled_assessment_id"' "${summary_body}"; then
  echo "evidence-summary missing most_recent_labeled_assessment_id (Phase 79/80)" >&2
  exit 1
fi
if ! grep -q '"most_recent_labeled_outcome_label"' "${summary_body}"; then
  echo "evidence-summary missing most_recent_labeled_outcome_label (Phase 79/80)" >&2
  exit 1
fi
echo "OK  Phase 80 most_recent_labeled_* fields present"
# Phase 146: scan-wide labeled/unlabeled counts from Phase 145.
if ! grep -q '"labeled_assessment_count"' "${summary_body}"; then
  echo "evidence-summary missing labeled_assessment_count (Phase 145/146)" >&2
  exit 1
fi
if ! grep -q '"unlabeled_assessment_count"' "${summary_body}"; then
  echo "evidence-summary missing unlabeled_assessment_count (Phase 145/146)" >&2
  exit 1
fi
echo "OK  Phase 146 scan-wide labeled/unlabeled assessment counts present"
# Phase 148: latest_coverage_confidence from Phase 147 (null OK).
if ! grep -q '"latest_coverage_confidence"' "${summary_body}"; then
  echo "evidence-summary missing latest_coverage_confidence (Phase 147/148)" >&2
  exit 1
fi
echo "OK  Phase 148 latest_coverage_confidence field present"
# Phase 150: latest_research_index from Phase 149 (null OK).
if ! grep -q '"latest_research_index"' "${summary_body}"; then
  echo "evidence-summary missing latest_research_index (Phase 149/150)" >&2
  exit 1
fi
echo "OK  Phase 150 latest_research_index field present"
# Phase 152: latest_as_of_trading_date from Phase 151 (null OK).
if ! grep -q '"latest_as_of_trading_date"' "${summary_body}"; then
  echo "evidence-summary missing latest_as_of_trading_date (Phase 151/152)" >&2
  exit 1
fi
echo "OK  Phase 152 latest_as_of_trading_date field present"
# Phase 154: latest_bar_count from Phase 153 (null OK).
if ! grep -q '"latest_bar_count"' "${summary_body}"; then
  echo "evidence-summary missing latest_bar_count (Phase 153/154)" >&2
  exit 1
fi
echo "OK  Phase 154 latest_bar_count field present"
# Phase 156: latest_input_source from Phase 155 (null OK).
if ! grep -q '"latest_input_source"' "${summary_body}"; then
  echo "evidence-summary missing latest_input_source (Phase 155/156)" >&2
  exit 1
fi
echo "OK  Phase 156 latest_input_source field present"
# Phase 158: latest_method_id from Phase 157 (null OK).
if ! grep -q '"latest_method_id"' "${summary_body}"; then
  echo "evidence-summary missing latest_method_id (Phase 157/158)" >&2
  exit 1
fi
echo "OK  Phase 158 latest_method_id field present"
# Phase 160: latest_method_version from Phase 159 (null OK).
if ! grep -q '"latest_method_version"' "${summary_body}"; then
  echo "evidence-summary missing latest_method_version (Phase 159/160)" >&2
  exit 1
fi
echo "OK  Phase 160 latest_method_version field present"
# Phase 162: latest_lookback_end_date from Phase 161 (null OK).
if ! grep -q '"latest_lookback_end_date"' "${summary_body}"; then
  echo "evidence-summary missing latest_lookback_end_date (Phase 161/162)" >&2
  exit 1
fi
echo "OK  Phase 162 latest_lookback_end_date field present"
# Phase 164: latest_lookback_start_date from Phase 163 (null OK).
if ! grep -q '"latest_lookback_start_date"' "${summary_body}"; then
  echo "evidence-summary missing latest_lookback_start_date (Phase 163/164)" >&2
  exit 1
fi
echo "OK  Phase 164 latest_lookback_start_date field present"
# Phase 166: latest_schema_version from Phase 165 (null OK).
if ! grep -q '"latest_schema_version"' "${summary_body}"; then
  echo "evidence-summary missing latest_schema_version (Phase 165/166)" >&2
  exit 1
fi
echo "OK  Phase 166 latest_schema_version field present"
# Phase 168: latest_computed_at from Phase 167 (null OK).
if ! grep -q '"latest_computed_at"' "${summary_body}"; then
  echo "evidence-summary missing latest_computed_at (Phase 167/168)" >&2
  exit 1
fi
echo "OK  Phase 168 latest_computed_at field present"
# Phase 170: latest_event_time from Phase 169 (null OK).
if ! grep -q '"latest_event_time"' "${summary_body}"; then
  echo "evidence-summary missing latest_event_time (Phase 169/170)" >&2
  exit 1
fi
echo "OK  Phase 170 latest_event_time field present"
# Phase 172: latest_probability_confidence from Phase 171 (null OK).
if ! grep -q '"latest_probability_confidence"' "${summary_body}"; then
  echo "evidence-summary missing latest_probability_confidence (Phase 171/172)" >&2
  exit 1
fi
echo "OK  Phase 172 latest_probability_confidence field present"
# Phase 174: latest_assessment_id from Phase 173 (null OK).
if ! grep -q '"latest_assessment_id"' "${summary_body}"; then
  echo "evidence-summary missing latest_assessment_id (Phase 173/174)" >&2
  exit 1
fi
echo "OK  Phase 174 latest_assessment_id field present"
# Phase 176: latest_outcome_label_id from Phase 175 (null OK).
if ! grep -q '"latest_outcome_label_id"' "${summary_body}"; then
  echo "evidence-summary missing latest_outcome_label_id (Phase 175/176)" >&2
  exit 1
fi
echo "OK  Phase 176 latest_outcome_label_id field present"
# Phase 178: latest_calibration_id from Phase 177 (null OK).
if ! grep -q '"latest_calibration_id"' "${summary_body}"; then
  echo "evidence-summary missing latest_calibration_id (Phase 177/178)" >&2
  exit 1
fi
echo "OK  Phase 178 latest_calibration_id field present"
# Phase 180: latest_calibration_horizon_key from Phase 179 (null OK).
if ! grep -q '"latest_calibration_horizon_key"' "${summary_body}"; then
  echo "evidence-summary missing latest_calibration_horizon_key (Phase 179/180)" >&2
  exit 1
fi
echo "OK  Phase 180 latest_calibration_horizon_key field present"
# Phase 182: latest_calibration_computed_at from Phase 181 (null OK).
if ! grep -q '"latest_calibration_computed_at"' "${summary_body}"; then
  echo "evidence-summary missing latest_calibration_computed_at (Phase 181/182)" >&2
  exit 1
fi
echo "OK  Phase 182 latest_calibration_computed_at field present"
# Phase 184: latest_calibration_corpus_count from Phase 183 (null OK).
if ! grep -q '"latest_calibration_corpus_count"' "${summary_body}"; then
  echo "evidence-summary missing latest_calibration_corpus_count (Phase 183/184)" >&2
  exit 1
fi
echo "OK  Phase 184 latest_calibration_corpus_count field present"
# Phase 186: latest_calibration_bucket_count from Phase 185 (null OK).
if ! grep -q '"latest_calibration_bucket_count"' "${summary_body}"; then
  echo "evidence-summary missing latest_calibration_bucket_count (Phase 185/186)" >&2
  exit 1
fi
echo "OK  Phase 186 latest_calibration_bucket_count field present"
# Phase 188: latest_calibration_method_id from Phase 187 (null OK).
if ! grep -q '"latest_calibration_method_id"' "${summary_body}"; then
  echo "evidence-summary missing latest_calibration_method_id (Phase 187/188)" >&2
  exit 1
fi
echo "OK  Phase 188 latest_calibration_method_id field present"
# Phase 190: latest_calibration_method_version from Phase 189 (null OK).
if ! grep -q '"latest_calibration_method_version"' "${summary_body}"; then
  echo "evidence-summary missing latest_calibration_method_version (Phase 189/190)" >&2
  exit 1
fi
echo "OK  Phase 190 latest_calibration_method_version field present"
# Phase 192: latest_calibration_schema_version from Phase 191 (null OK).
if ! grep -q '"latest_calibration_schema_version"' "${summary_body}"; then
  echo "evidence-summary missing latest_calibration_schema_version (Phase 191/192)" >&2
  exit 1
fi
echo "OK  Phase 192 latest_calibration_schema_version field present"
# Phase 194: latest_calibration_state from Phase 193 (null OK).
if ! grep -q '"latest_calibration_state"' "${summary_body}"; then
  echo "evidence-summary missing latest_calibration_state (Phase 193/194)" >&2
  exit 1
fi
echo "OK  Phase 194 latest_calibration_state field present"
# Phase 196: latest_calibration_probability_confidence from Phase 195 (null OK).
if ! grep -q '"latest_calibration_probability_confidence"' "${summary_body}"; then
  echo "evidence-summary missing latest_calibration_probability_confidence (Phase 195/196)" >&2
  exit 1
fi
echo "OK  Phase 196 latest_calibration_probability_confidence field present"
# Phase 198: latest_calibration_assessment_snapshot_id from Phase 197 (null OK).
if ! grep -q '"latest_calibration_assessment_snapshot_id"' "${summary_body}"; then
  echo "evidence-summary missing latest_calibration_assessment_snapshot_id (Phase 197/198)" >&2
  exit 1
fi
echo "OK  Phase 198 latest_calibration_assessment_snapshot_id field present"
# Phase 27/31: log present label and end-date keys only (never invent).
if printf '%s' "${summary_body}" | grep -q '"latest_outcome_label"[[:space:]]*:[[:space:]]*null'; then
  echo "OK  evidence-summary state=research_only label_keys=(none) end_date_keys=(none)"
else
  if printf '%s' "${summary_body}" | grep -q '"labels"[[:space:]]*:[[:space:]]*{[^}]*}'; then
    keys="$(printf '%s' "${summary_body}" | grep -oE '"forward_return_[0-9]+"' | tr -d '"' | sort -u | paste -sd, -)"
    if [[ -z "${keys}" ]]; then keys="(none-or-empty)"; fi
  else
    keys="(none-or-empty)"
  fi
  if printf '%s' "${summary_body}" | grep -q '"label_end_dates"[[:space:]]*:[[:space:]]*null\|"label_end_dates"[[:space:]]*:[[:space:]]*{}'; then
    end_keys="(none)"
  elif printf '%s' "${summary_body}" | grep -q '"label_end_dates"'; then
    end_keys="$(printf '%s' "${summary_body}" | grep -oE '"forward_return_[0-9]+"' | tr -d '"' | sort -u | paste -sd, -)"
    if [[ -z "${end_keys}" ]]; then end_keys="(none)"; fi
  else
    end_keys="(none)"
  fi
  echo "OK  evidence-summary state=research_only label_keys=${keys} end_date_keys=${end_keys}"
fi

export_url="${API}/research/${VERIFY_SYMBOL}/evidence-summary/export"
export_body="$(mktemp)"
export_headers="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_export_body}" "${ready_export_headers}" "${assess_body}" "${assess_export_body}" "${assess_export_headers}" "${calib_body}" "${label_body}" "${label_export_body}" "${label_export_headers}" "${calib_export_body}" "${calib_export_headers}" "${summary_body}" "${export_body}" "${export_headers}"; }
trap cleanup EXIT
export_code="$(
  curl -sS "${CURL_INSECURE[@]}" -D "${export_headers}" -o "${export_body}" -w "%{http_code}" --max-time 30 \
    -b "${COOKIE_JAR}" -H "Accept: application/json" "${export_url}"
)"
assert_status "GET ${export_url} (auth)" "${export_code}" 200
if ! grep -qi 'content-disposition:.*attachment' "${export_headers}"; then
  echo "evidence-summary/export missing Content-Disposition attachment" >&2
  exit 1
fi
if ! grep -q '"state"[[:space:]]*:[[:space:]]*"research_only"' "${export_body}"; then
  echo "evidence-summary/export missing state=research_only" >&2
  exit 1
fi
if ! grep -q '"by_horizon"' "${export_body}"; then
  echo "evidence-summary/export.calibration_readiness missing by_horizon (Phase 75)" >&2
  exit 1
fi
if ! grep -q 'forward_return_5' "${export_body}" || ! grep -q 'forward_return_20' "${export_body}"; then
  echo "evidence-summary/export.calibration_readiness.by_horizon missing forward_return_5/20 (Phase 75)" >&2
  exit 1
fi
for field in corpus_count bucket_count min_corpus min_bucket; do
  if ! grep -q "\"${field}\"" "${export_body}"; then
    echo "evidence-summary/export.calibration_readiness missing ${field} (Phase 76)" >&2
    exit 1
  fi
done
if ! grep -q '"most_recent_labeled_assessment_id"' "${export_body}"; then
  echo "evidence-summary/export missing most_recent_labeled_assessment_id (Phase 79/80)" >&2
  exit 1
fi
if ! grep -q '"most_recent_labeled_outcome_label"' "${export_body}"; then
  echo "evidence-summary/export missing most_recent_labeled_outcome_label (Phase 79/80)" >&2
  exit 1
fi
echo "OK  evidence-summary/export attachment state=research_only"

mapfile -t COMPOSE_FILES < <(compose_nas_file_flags "${REPO_ROOT}")
COMPOSE_FILE_ARGS="${COMPOSE_FILES[*]}"

if [[ -n "${AEGIS_NAS_SSH_HOST:-}" \
   && "${AEGIS_NAS_SSH_HOST}" != replace-with-* \
   && "${AEGIS_NAS_SSH_HOST}" != your-* \
   && -n "${AEGIS_NAS_SSH_USER:-}" \
   && -n "${AEGIS_NAS_REMOTE_DIR:-}" ]]; then
  echo "==> Alembic current (via SSH)"
  REMOTE="${AEGIS_NAS_SSH_USER}@${AEGIS_NAS_SSH_HOST}"
  REMOTE_DIR="${AEGIS_NAS_REMOTE_DIR%/}"
  mapfile -t SSH_ARGS < <(ssh_base_args)
  out="$(ssh "${SSH_ARGS[@]}" "${REMOTE}" bash -s <<EOF
set -euo pipefail
cd '${REMOTE_DIR}'
docker compose ${COMPOSE_FILE_ARGS} --env-file .env.nas --project-directory . exec -T backend alembic current
EOF
)"
  echo "${out}"
  if ! echo "${out}" | grep -Eq '0009|head'; then
    echo "error: Alembic current did not report migration 0009 / head." >&2
    exit 1
  fi
  echo "OK  alembic current includes 0009 / head"
  echo "==> Phase 52 research bar load setting (via SSH)"
  ssh "${SSH_ARGS[@]}" "${REMOTE}" bash -s <<EOF
set -euo pipefail
cd '${REMOTE_DIR}'
if grep -E '^AEGIS_RESEARCH_BAR_LOAD_LIMIT=[0-9]+' .env.nas >/dev/null; then
  grep -E '^AEGIS_RESEARCH_BAR_LOAD_LIMIT=' .env.nas
else
  echo 'AEGIS_RESEARCH_BAR_LOAD_LIMIT missing from .env.nas' >&2
  exit 1
fi
val="\$(grep -E '^AEGIS_RESEARCH_BAR_LOAD_LIMIT=' .env.nas | head -n1 | cut -d= -f2)"
if [ "\$val" -lt 40 ] || [ "\$val" -gt 2000 ]; then
  echo "AEGIS_RESEARCH_BAR_LOAD_LIMIT out of bounds: \$val" >&2
  exit 1
fi
EOF
  echo "OK  AEGIS_RESEARCH_BAR_LOAD_LIMIT present on NAS .env.nas"
  echo "==> Phase 54 daily bar output size (via SSH)"
  ssh "${SSH_ARGS[@]}" "${REMOTE}" bash -s <<EOF
set -euo pipefail
cd '${REMOTE_DIR}'
val="\$(grep -E '^AEGIS_DAILY_BAR_OUTPUT_SIZE=' .env.nas | head -n1 | cut -d= -f2 | tr -d '[:space:]')"
if [ "\$val" != "full" ]; then
  echo "AEGIS_DAILY_BAR_OUTPUT_SIZE must be full (got: \$val)" >&2
  exit 1
fi
echo "AEGIS_DAILY_BAR_OUTPUT_SIZE=\$val"
EOF
  echo "OK  AEGIS_DAILY_BAR_OUTPUT_SIZE=full on NAS .env.nas"
  echo "==> Phase 56 research cross-source fill (via SSH)"
  ssh "${SSH_ARGS[@]}" "${REMOTE}" bash -s <<EOF
set -euo pipefail
cd '${REMOTE_DIR}'
if grep -E '^AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=true' .env.nas >/dev/null; then
  grep -E '^AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=' .env.nas
else
  echo 'AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL must be true on .env.nas' >&2
  exit 1
fi
EOF
  echo "OK  AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=true on NAS .env.nas"
  if nas_tls_enabled; then
    echo "==> Caddy service (TLS profile)"
    ssh "${SSH_ARGS[@]}" "${REMOTE}" bash -s <<EOF
set -euo pipefail
cd '${REMOTE_DIR}'
docker compose ${COMPOSE_FILE_ARGS} --env-file .env.nas --project-directory . ps --status running caddy | grep -E 'caddy' >/dev/null
EOF
    echo "OK  caddy service is running"
  fi
  echo
  echo "Log inspection guidance (run on NAS or via SSH):"
  echo "  docker compose ${COMPOSE_FILE_ARGS} --env-file .env.nas logs --tail=200 backend"
  echo "  docker compose ${COMPOSE_FILE_ARGS} --env-file .env.nas logs --tail=200 frontend"
  if nas_tls_enabled; then
    echo "  docker compose ${COMPOSE_FILE_ARGS} --env-file .env.nas logs --tail=200 caddy"
  fi
  echo "  docker compose ${COMPOSE_FILE_ARGS} --env-file .env.nas ps"
else
  echo
  echo "NOTE: SSH vars not fully set; skipped remote Alembic check."
  echo "On the NAS, confirm: docker compose ... exec -T backend alembic current"
  echo "Expect revision 0008 (research_assessment_probability_calibrations) / head."
fi

echo
echo "LIVE VERIFICATION PASSED for HTTP(S) checks against ${API} and ${FRONTEND} (symbol=${VERIFY_SYMBOL})."
echo "Upload/start alone is never sufficient; this verify step is the acceptance evidence."
echo "Evidence: retain this stdout. Dry-run runs are not evidence."
