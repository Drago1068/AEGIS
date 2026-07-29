#!/usr/bin/env bash
# Local dry-run for NAS packaging without a live NAS (Phase 7).
# Usage: ./docker/nas/scripts/validate-local.sh [--build-images]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
BUILD_IMAGES=0
if [[ "${1:-}" == "--build-images" ]]; then
  BUILD_IMAGES=1
fi

ENV_FILE="${REPO_ROOT}/.env.nas"
USING_EXAMPLE=0
if [[ ! -f "${ENV_FILE}" ]]; then
  ENV_FILE="${REPO_ROOT}/.env.nas.example"
  USING_EXAMPLE=1
  echo "NOTE: .env.nas not found; using .env.nas.example for config dry-run only."
fi

COMPOSE_ARGS=(
  -f "${REPO_ROOT}/docker-compose.yml"
  -f "${REPO_ROOT}/docker/nas/docker-compose.nas.yml"
  --env-file "${ENV_FILE}"
  --project-directory "${REPO_ROOT}"
)

echo "==> docker compose config (NAS overlay)"
docker compose "${COMPOSE_ARGS[@]}" config --quiet
echo "OK  compose config"

if [[ "${BUILD_IMAGES}" -eq 1 ]]; then
  if [[ "${USING_EXAMPLE}" -eq 1 ]]; then
    echo "error: refusing amd64 image build with .env.nas.example placeholders." >&2
    echo "Copy to .env.nas, set real non-default secrets and NEXT_PUBLIC_API_BASE_URL, then re-run." >&2
    exit 1
  fi
  load_dotenv_file "${ENV_FILE}"
  require_env_vars \
    NEXT_PUBLIC_API_BASE_URL \
    AEGIS_CORS_ORIGINS \
    AEGIS_OPERATOR_PASSWORD \
    POSTGRES_PASSWORD
  assert_nas_secrets_not_placeholders
  echo "==> Building linux/amd64 images (no push, no deploy)"
  docker compose "${COMPOSE_ARGS[@]}" build
  echo "OK  amd64 build"
else
  echo "Skipped image build (pass --build-images to build linux/amd64 locally)."
fi

echo
echo "Local NAS packaging dry-run succeeded. No NAS was contacted."
