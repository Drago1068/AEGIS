#!/usr/bin/env bash
# Local dry-run for NAS packaging without a live NAS (Phase 7 + optional Phase 9 TLS).
# Usage: ./docker/nas/scripts/validate-local.sh [--build-images] [--tls]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
BUILD_IMAGES=0
FORCE_TLS=0
for arg in "$@"; do
  case "${arg}" in
    --build-images) BUILD_IMAGES=1 ;;
    --tls) FORCE_TLS=1 ;;
    *)
      echo "usage: $0 [--build-images] [--tls]" >&2
      exit 1
      ;;
  esac
done

ENV_FILE="${REPO_ROOT}/.env.nas"
USING_EXAMPLE=0
if [[ ! -f "${ENV_FILE}" ]]; then
  ENV_FILE="${REPO_ROOT}/.env.nas.example"
  USING_EXAMPLE=1
  echo "NOTE: .env.nas not found; using .env.nas.example for config dry-run only."
fi

load_dotenv_file "${ENV_FILE}"

if [[ "${FORCE_TLS}" -eq 1 ]]; then
  export AEGIS_NAS_TLS_ENABLED=true
fi

COMPOSE_ARGS=(
  -f "${REPO_ROOT}/docker-compose.yml"
  -f "${REPO_ROOT}/docker/nas/docker-compose.nas.yml"
  --env-file "${ENV_FILE}"
  --project-directory "${REPO_ROOT}"
)

echo "==> docker compose config (NAS overlay)"
docker compose "${COMPOSE_ARGS[@]}" config --quiet
echo "OK  compose config (base NAS overlay)"

if nas_tls_enabled; then
  echo "==> TLS profile selected — validating material and TLS overlay config"
  if [[ "${USING_EXAMPLE}" -eq 1 ]]; then
    assert_tls_profile_ready "${REPO_ROOT}" --allow-example-placeholders
  else
    assert_tls_profile_ready "${REPO_ROOT}"
  fi
  TLS_ARGS=(
    -f "${REPO_ROOT}/docker-compose.yml"
    -f "${REPO_ROOT}/docker/nas/docker-compose.nas.yml"
    -f "${REPO_ROOT}/docker/nas/docker-compose.nas.tls.yml"
    --env-file "${ENV_FILE}"
    --project-directory "${REPO_ROOT}"
  )
  docker compose "${TLS_ARGS[@]}" config --quiet
  echo "OK  compose config (NAS + TLS overlay)"
else
  echo "Skipped TLS overlay (set AEGIS_NAS_TLS_ENABLED=true or pass --tls to validate)."
fi

if [[ "${BUILD_IMAGES}" -eq 1 ]]; then
  if [[ "${USING_EXAMPLE}" -eq 1 ]]; then
    echo "error: refusing amd64 image build with .env.nas.example placeholders." >&2
    echo "Copy to .env.nas, set real non-default secrets and NEXT_PUBLIC_API_BASE_URL, then re-run." >&2
    exit 1
  fi
  require_env_vars \
    NEXT_PUBLIC_API_BASE_URL \
    AEGIS_CORS_ORIGINS \
    AEGIS_OPERATOR_PASSWORD \
    POSTGRES_PASSWORD
  assert_nas_secrets_not_placeholders
  if nas_tls_enabled; then
    assert_tls_profile_ready "${REPO_ROOT}"
  fi
  echo "==> Building linux/amd64 images (no push, no deploy)"
  mapfile -t BUILD_ARGS < <(compose_nas_args "${REPO_ROOT}" "${ENV_FILE}")
  docker compose "${BUILD_ARGS[@]}" build
  echo "OK  amd64 build"
else
  echo "Skipped image build (pass --build-images to build linux/amd64 locally)."
fi

echo
echo "Local NAS packaging dry-run succeeded. No NAS was contacted."
