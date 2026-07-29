#!/usr/bin/env bash
# Verify a live AEGIS NAS deployment (Phase 7). Distinct from package upload / deploy start.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
ENV_NAS="${REPO_ROOT}/.env.nas"
load_dotenv_file "${ENV_NAS}"
require_env_vars AEGIS_NAS_API_BASE_URL AEGIS_NAS_FRONTEND_BASE_URL

API="${AEGIS_NAS_API_BASE_URL%/}"
FRONTEND="${AEGIS_NAS_FRONTEND_BASE_URL%/}"

if [[ "${API}" == *replace-with-* || "${FRONTEND}" == *replace-with-* ]]; then
  echo "error: AEGIS_NAS_API_BASE_URL / AEGIS_NAS_FRONTEND_BASE_URL still look like placeholders." >&2
  exit 1
fi

http_status() {
  local url="$1"
  curl -sS -o /dev/null -w "%{http_code}" --max-time 30 "${url}"
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

echo "==> Public health and readiness"
assert_status "GET ${API}/health" "$(http_status "${API}/health")" 200
assert_status "GET ${API}/ready" "$(http_status "${API}/ready")" 200

echo "==> Auth gate (expect 401 without session)"
assert_status "GET ${API}/watchlist" "$(http_status "${API}/watchlist")" 401
assert_status "GET ${API}/market-data/AAPL/daily-bars" "$(http_status "${API}/market-data/AAPL/daily-bars")" 401
assert_status "GET ${API}/research/AAPL/assessments/latest" "$(http_status "${API}/research/AAPL/assessments/latest")" 401

echo "==> Frontend reachability"
fe_status="$(http_status "${FRONTEND}")"
assert_status "GET ${FRONTEND}" "${fe_status}" 200 307 308 302

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
docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml --env-file .env.nas --project-directory . exec -T backend alembic current
EOF
)"
  echo "${out}"
  if ! echo "${out}" | grep -Eq '0005|head'; then
    echo "error: Alembic current did not report migration 0005 / head." >&2
    exit 1
  fi
  echo "OK  alembic current includes 0005 / head"
  echo
  echo "Log inspection guidance (run on NAS or via SSH):"
  echo "  docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml --env-file .env.nas logs --tail=200 backend"
  echo "  docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml --env-file .env.nas logs --tail=200 frontend"
  echo "  docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml --env-file .env.nas ps"
else
  echo
  echo "NOTE: SSH vars not fully set; skipped remote Alembic check."
  echo "On the NAS, confirm: docker compose ... exec -T backend alembic current"
  echo "Expect revision 0005 (research_assessment_snapshots) / head."
fi

echo
echo "Verification passed for HTTP checks against ${API} and ${FRONTEND}."
echo "Upload/start alone is never sufficient; this verify step is the acceptance evidence."
