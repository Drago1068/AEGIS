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
  echo "  3. Auth gate 401: watchlist, daily-bars, research latest, assessments list(+export), calibration-readiness(+export), outcome-labels/export, calibrations/export, evidence-summary(+export), outcome-labels/backfill POST"
  echo "  4. Frontend base URL -> 200|302|307|308"
  echo "  5. POST /auth/login (operator credentials from .env.nas) -> 200 + cookie"
  echo "  6. Authenticated GET /research/${symbol}/calibration-readiness -> 200 (by_horizon includes fwd5+fwd20)"
  echo "  7. Authenticated GET /research/${symbol}/calibration-readiness/export -> 200 (attachment; by_horizon present)"
  echo "  8. Authenticated GET /research/${symbol}/assessments/latest -> 200|404"
  echo "  9. Authenticated GET /research/${symbol}/assessments?limit= -> 200 (JSON array; [] OK)"
  echo " 10. Authenticated GET /research/${symbol}/assessments/export -> 200 (attachment, JSON array; [] OK)"
  echo " 11. Authenticated POST /research/${symbol}/outcome-labels/backfill -> 200 (summary counts; zeros OK)"
  echo " 12. Authenticated POST .../assessments/{id}/calibrations?horizon=forward_return_5 -> 200|422"
  echo " 13. Authenticated GET .../assessments/{id}/calibrations and .../outcome-labels -> 200 (JSON array; [] OK)"
  echo " 14. Authenticated GET .../assessments/{id}/outcome-labels/export -> 200 (attachment, JSON array; [] OK)"
  echo " 15. Authenticated GET .../assessments/{id}/calibrations/export -> 200 (attachment, JSON array; [] OK)"
  echo " 16. Authenticated GET /research/${symbol}/evidence-summary -> 200 (state=research_only; log present label + end-date keys when any)"
  echo " 17. Authenticated GET /research/${symbol}/evidence-summary/export -> 200 (attachment, state=research_only)"
  echo " 18. SSH alembic current includes 0009|head (when SSH configured)"
  echo " 19. TLS profile: https:// URLs + Secure cookies when enabled"
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

backfill_url="${API}/research/${VERIFY_SYMBOL}/outcome-labels/backfill?limit=20"
backfill_body="$(mktemp)"
cleanup() { rm -f "${COOKIE_JAR}" "${ready_body}" "${ready_export_body}" "${ready_export_headers}" "${assess_body}" "${assess_export_body}" "${assess_export_headers}" "${backfill_body}"; }
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
echo "OK  outcome-labels/backfill summary counts present"

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
